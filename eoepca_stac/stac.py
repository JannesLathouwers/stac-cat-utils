import datetime
import logging
import os
import sys

import pystac
import warnings

from eoepca_stac import stac_generic
from eoepca_stac.utils import is_product_folder, is_collection_empty, convert_paths
from rasterio.errors import RasterioIOError, RasterioError
from eoepca_stac.slc import stac as stac_sentinel1_slc
from stactools.sentinel1.grd import stac as stac_sentinel1_grd
from stactools.sentinel2 import stac as stac_sentinel2
from stactools.landsat import stac as stac_landsat

warnings.filterwarnings('ignore')

logger = logging.getLogger("EoepcaStacGenerator")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

default_collection_extent = pystac.Extent(spatial=pystac.SpatialExtent([-180, -90, 180, 90]),
                                          temporal=pystac.TemporalExtent([[None, None]]))


class EoepcaStacGenerator:
    def __init__(self):
        self.__stac_catalog: pystac.Catalog = None
        self.__catalog_name = 'stac_catalog'
        self.__generic_collection = pystac.Collection(id='Files',
                                                      description='Collection of generic files',
                                                      extent=default_collection_extent)

    @staticmethod
    def __handle_product_stac_item(product, base_path, stac_container):
        if product[1] == 'S1':
            if product[2] == 'GRD':
                sentinel1_grd_item = stac_sentinel1_grd.create_item(base_path)
                stac_container.add_item(sentinel1_grd_item)
            if product[2] == 'SLC':
                sentinel1_slc_item = stac_sentinel1_slc.create_item(base_path)
                stac_container.add_item(sentinel1_slc_item)
        if product[1] == 'S2':
            sentinel2_item = stac_sentinel2.create_item(base_path)
            stac_container.add_item(sentinel2_item)
        if product[1] == 'LANDSAT':
            landsat_item = stac_landsat.create_item(os.path.join(base_path, product[2]))
            stac_container.add_item(landsat_item)

    @staticmethod
    def __handle_file_stac(path, container):
        def add_to_container(c, element):
            if isinstance(c, pystac.Collection) and isinstance(element, pystac.Asset):
                c.add_asset(element.title, element)
            elif isinstance(c, pystac.Collection) and isinstance(element, pystac.Item):
                c.add_item(element)
            elif isinstance(c, pystac.Item):
                if isinstance(element, pystac.Asset):
                    c.add_asset(element.title, element)
                else:
                    c.assets = {**c.assets, **element.assets}
            else:
                # Warn about unexpected behavior
                logger.warning(f'{element} has not been added to {container}')
        try:
            item = stac_generic.create_image_item(path, with_proj=True, with_eo=True, with_raster=True)
            add_to_container(container, item)
        except (RasterioIOError, RasterioError):
            item = stac_generic.create_file_item(path)
            add_to_container(container, item)

    def populate_catalog(self, base_path, collection_paths, item_paths, ignore_paths, stac_container=None):
        default_container = stac_container or self.__stac_catalog

        if base_path in ignore_paths:
            # Ignore element to be ignored in the given ignore lists
            return
        else:
            # Check if current element should be an item or a collection
            if base_path in item_paths:
                collection = pystac.Item(id=os.path.basename(base_path), geometry=None, bbox=None,
                                         datetime=datetime.datetime.now(), properties={})
                default_container.add_item(collection)
            elif base_path in collection_paths:
                collection = pystac.Collection(id=os.path.basename(base_path), description='Collection of files',
                                               extent=default_collection_extent)
                default_container.add_child(collection)
            else:
                collection = stac_container

        product = is_product_folder(base_path)
        if product[0]:
            # Handle and create STAC item for recognized product folder
            self.__handle_product_stac_item(product, base_path, default_container)
            return

        for entry in os.listdir(base_path):
            path = os.path.join(base_path, entry)
            if os.path.isdir(path):
                # Handle folder recursively
                container = collection or stac_container
                self.populate_catalog(path, collection_paths, item_paths, ignore_paths, stac_container=container)

            if os.path.isfile(path):
                # Handle files and add them to the right container (Collection/Item)
                container = collection or self.__generic_collection
                logger.debug(f'{path} added to {container}')
                self.__handle_file_stac(path, container)

    def create(
        self, src_path, catalog_name='Catalog', collection_paths=None, item_paths=None, ignore_paths=None
    ):
        self.__catalog_name = catalog_name
        self.__stac_catalog = pystac.Catalog(id=self.__catalog_name,
                                             description=f'STAC Catalog for {os.path.basename(src_path)}')
        self.populate_catalog(src_path,
                              convert_paths(collection_paths),
                              convert_paths(item_paths),
                              convert_paths(ignore_paths))
        if not is_collection_empty(self.__generic_collection):
            self.__stac_catalog.add_child(self.__generic_collection)
        return self.__stac_catalog

    def save(self, dest_path=None, href_base_path=None):
        dest_path = dest_path or f'stac_{self.__catalog_name.lower()}'
        self.__stac_catalog.normalize_hrefs(dest_path)
        self.__stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
