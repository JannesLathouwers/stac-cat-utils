import datetime
import logging
import os
import sys

import pystac
import warnings

from eoepca_stac import stac_generic
from eoepca_stac.utils import is_product_folder, is_collection_empty, generate_path_list, collection_to_assets
from rasterio.errors import RasterioIOError, RasterioError
from eoepca_stac.slc import stac as stac_sentinel1_slc
from stactools.sentinel1.grd import stac as stac_sentinel1_grd
from stactools.sentinel2 import stac as stac_sentinel2
from stactools.landsat import stac as stac_landsat
from typing import Optional

warnings.filterwarnings('ignore')

logger = logging.getLogger("EoepcaStacGenerator")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)

default_extent = pystac.Extent(spatial=pystac.SpatialExtent([-180, -90, 180, 90]),
                               temporal=pystac.TemporalExtent([[None, None]]))


class EoepcaStacGenerator:
    def __init__(self):
        self.__stac_catalog: Optional[pystac.Catalog] = None
        self.__src_path = None
        self.__asset_href_prefix = '/'
        self.__catalog_name = 'stac_catalog'
        self.__generic_collection = pystac.Collection(id='Files',
                                                      description='Collection of generic files',
                                                      extent=default_extent)

    @staticmethod
    def __add_to_container(container, element):
        if isinstance(container, pystac.Collection):
            if isinstance(element, pystac.Asset):
                container.add_asset(element.title, element)
            elif isinstance(element, pystac.Item):
                container.add_item(element)
            elif isinstance(element, pystac.Collection):
                container.add_child(element)
        elif isinstance(container, pystac.Item):
            if isinstance(element, pystac.Asset):
                container.add_asset(element.title, element)
            elif isinstance(element, pystac.Item):
                container.assets = {**container.assets, **element.assets}
            else:
                container.assets = {**container.assets, **collection_to_assets(element)}
        elif isinstance(container, pystac.Catalog):
            if isinstance(element, pystac.Item):
                container.add_item(element)
            elif isinstance(element, pystac.Collection):
                container.add_child(element)
        else:
            # Warn about unexpected behavior
            logger.warning(f'{element} has not been added to {container}')

    def __handle_product_stac_item(self, product, base_path, container):
        if product['name'] == 'S1':
            if product['extra_info'] == 'GRD':
                sentinel1_grd_item = stac_sentinel1_grd.create_item(base_path)
                self.__add_to_container(container, sentinel1_grd_item)
            if product['extra_info'] == 'SLC':
                sentinel1_slc_item = stac_sentinel1_slc.create_item(base_path)
                self.__add_to_container(container, sentinel1_slc_item)
        if product['name'] == 'S2':
            sentinel2_item = stac_sentinel2.create_item(base_path)
            self.__add_to_container(container, sentinel2_item)
        if product['name'] == 'LANDSAT':
            landsat_item = stac_landsat.create_item(os.path.join(base_path, product['extra_info']))
            self.__add_to_container(container, landsat_item)

    def __handle_file_stac(self, path, container):
        try:
            item = stac_generic.create_image_item(path, asset_name=path, with_proj=True, with_eo=True, with_raster=True)
            self.__add_to_container(container, item)
        except (RasterioIOError, RasterioError):
            item = stac_generic.create_file_item(path)
            self.__add_to_container(container, item)

    @staticmethod
    def __get_container(base_path, collection_paths, item_paths, container):
        folder_name = os.path.basename(base_path)
        if base_path in collection_paths:
            container = pystac.Collection(id=folder_name,
                                          description=f'Collection of files under {folder_name}',
                                          extent=default_extent)
        elif base_path in item_paths:
            container = pystac.Item(id=folder_name,
                                    geometry=None, bbox=None,
                                    datetime=datetime.datetime.now(), properties={})
        return container

    def populate_catalog(self, base_path, collection_paths, item_paths, ignore_paths, parent_container=None):
        default_container = parent_container or self.__stac_catalog

        # Check if current folder should be a collection or an item
        base_path_container = self.__get_container(base_path, collection_paths, item_paths, parent_container)

        product = is_product_folder(base_path)
        if product['is_product']:
            # Handle and create STAC item for recognized product folder
            self.__handle_product_stac_item(product, base_path, default_container)
            return

        for entry in os.listdir(base_path):
            path = os.path.join(base_path, entry)
            if path in ignore_paths:
                continue

            if os.path.isdir(path):
                # Recursive handling of folders
                container = base_path_container
                self.populate_catalog(path, collection_paths, item_paths, ignore_paths, parent_container=container)

            if os.path.isfile(path):
                # Handle files and add them to the correct container
                container = base_path_container or self.__generic_collection
                file_path_container = self.__get_container(path, collection_paths, item_paths, container)
                logger.debug(f'{path} added to {file_path_container}')
                self.__handle_file_stac(path, file_path_container)
                if file_path_container != container:
                    self.__add_to_container(container, file_path_container)

        if base_path_container != parent_container:
            self.__add_to_container(default_container, base_path_container)

    def __clean(self):
        def clean(assets_dict):
            return {k: d for k, d in assets_dict.items() if os.path.exists(d.href)}

        for i in self.__stac_catalog.get_all_collections():
            i.assets = clean(i.assets)
        for i in self.__stac_catalog.get_all_items():
            i.assets = clean(i.assets)

    def update_asset_href(self, asset_href_prefix=None):
        self.__asset_href_prefix = asset_href_prefix or self.__asset_href_prefix

        def add_asset_href_prefix(assets_dict):
            def update_asset_href(asset: pystac.Asset):
                asset.href = f'{self.__asset_href_prefix}{asset.href}'
                return asset

            return {k: update_asset_href(d) for k, d in assets_dict.items()}

        for i in self.__stac_catalog.get_all_collections():
            i.set_self_href(self.__src_path)
            i.make_all_asset_hrefs_relative()
            i.assets = add_asset_href_prefix(i.assets)
        for i in self.__stac_catalog.get_all_items():
            i.set_self_href(self.__src_path)
            i.make_asset_hrefs_relative()
            i.assets = add_asset_href_prefix(i.assets)

    def create(
            self, src_path, catalog_name='Catalog', collection_paths=None, item_paths=None, ignore_paths=None,
            asset_href_prefix=None
    ):
        self.__src_path = src_path
        self.__asset_href_prefix = asset_href_prefix or self.__asset_href_prefix
        self.__catalog_name = catalog_name
        self.__stac_catalog = pystac.Catalog(id=self.__catalog_name,
                                             description=f'STAC Catalog for {os.path.basename(src_path)}')
        if src_path in generate_path_list(ignore_paths):
            return self.__stac_catalog

        self.populate_catalog(src_path,
                              generate_path_list(collection_paths),
                              generate_path_list(item_paths),
                              generate_path_list(ignore_paths))

        if not is_collection_empty(self.__generic_collection):
            self.__stac_catalog.add_child(self.__generic_collection)

        self.__clean()
        self.update_asset_href()

        return self.__stac_catalog

    def save(self, dest_path=None, asset_href_prefix='/'):
        if not self.__src_path:
            logger.error('Stac catalog must be created first using "create" method')
        dest_path = dest_path or f'stac_{self.__catalog_name.lower()}'
        self.__stac_catalog.normalize_hrefs(dest_path)
        if asset_href_prefix != self.__asset_href_prefix:
            self.update_asset_href(asset_href_prefix)
        self.__stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
