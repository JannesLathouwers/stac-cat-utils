import logging
import os
import re
import pystac

from glob import glob
from lxml import etree
from pystac import RequiredPropertyMissing
from pystac.extensions.datacube import DatacubeExtension, CollectionDatacubeExtension

logger = logging.getLogger('StacCatalogGenerator')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def is_product_folder(path):
    folder_name = os.path.basename(path)
    folder_content = os.listdir(path)

    if folder_name.startswith('S1') and 'manifest.safe' in folder_content:
        tree = etree.parse(os.path.join(path, 'manifest.safe'))
        elements = tree.findall('.//s1sarl1:productType', tree.getroot().nsmap)
        if len(elements) > 0 and elements[0].text == 'GRD':
            return {'is_product': True, 'name': 'S1', 'extra_info': 'GRD'}
        if len(elements) > 0 and elements[0].text == 'SLC':
            return {'is_product': True, 'name': 'S1', 'extra_info': 'SLC'}

    if folder_name.startswith('S2') and 'manifest.safe' in folder_content:
        tree = etree.parse(os.path.join(path, 'manifest.safe'))
        elements = tree.findall('.//*[@unitType="Product_Level-2A"]')
        if len(elements) > 0:
            return {'is_product': True, 'name': 'S2', 'extra_info': 'L2A'}
        elements = tree.findall('.//*[@unitType="Product_Level-1C"]')
        if len(elements) > 0:
            return {'is_product': True, 'name': 'S2', 'extra_info': 'L1C'}

    landsat_metadata = folder_name.split('_')
    if len(landsat_metadata) == 7 and landsat_metadata[0][0] == 'L':
        landsat_type = f'{landsat_metadata[0][2:]}{landsat_metadata[1][:2]}{landsat_metadata[5]}'
        if re.match(r'(0[1-5]L102|0[4579]L202)', landsat_type):
            for file in folder_content:
                if os.path.isfile(os.path.join(path, file)) and file.lower().endswith('mtl.xml'):
                    return {'is_product': True, 'name': 'LANDSAT', 'extra_info': file}
        else:
            logger.warning(f'Supported Landsat: Landsat 1-5 Collection 2 Level-1 or Landsat 4-5, 7-9 Collection 2 '
                           f'Level-2 scene data. {folder_name} will be handled as non product folder.')

    return {'is_product': False, 'name': None, 'extra_info': None}


def is_collection_empty(collection: pystac.Collection):
    return not(
        list(collection.get_all_items()) or collection.get_assets().keys() or list(collection.get_all_collections())
    )


def generate_path_list(path_list: list):
    """
    Convert a list of string, Path instance or glob Pattern to a list of concrete string paths
    """
    matches = []
    if path_list:
        for path in path_list:
            matches.extend(glob(os.path.normpath(str(path)), recursive=True))
    return matches


def collection_to_assets(collection: pystac.Collection):
    all_assets = collection.assets
    for col in collection.get_all_collections():
        all_assets = {**all_assets, **collection_to_assets(col)}
    for item in collection.get_all_items():
        all_assets = {**all_assets, **item.assets}
    return all_assets


def cube_extend(collection, key):
    if not isinstance(collection, CollectionDatacubeExtension):
        collection = DatacubeExtension.ext(collection, add_if_missing=True)
    try:
        value = getattr(collection, key)
        if not value:
            setattr(collection, key, {})
    except RequiredPropertyMissing:
        setattr(collection, key, {})
    return collection


def is_key_unique(collection, key):
    keys = []
    if getattr(collection, 'dimensions'):
        keys.extend(collection.dimensions.keys())
    if getattr(collection, 'variables'):
        keys.extend(collection.variables.keys())
    is_unique = key not in keys
    if not is_unique:
        logger.error(f'The key name {key} is already used in cube:dimensions or cube:variables.')
    return is_unique


def item_assets_info(item: pystac.Item):
    asset_names = []
    asset_bands = []
    for name, asset in item.assets.items():
        if asset.media_type.startswith('image/'):
            if 'eo:bands' in asset.extra_fields:
                asset_bands.extend(asset.extra_fields['eo:bands'])
                band_names = '_'.join([i['name'] for i in asset.extra_fields['eo:bands']])
                if 'proj:transform' in asset.extra_fields:
                    resolution = asset.extra_fields['proj:transform'][0]
                    asset_names.append(f'{band_names}-{resolution}')
                else:
                    asset_names.append(band_names)
            else:
                asset_names.append(name)
    return sorted(asset_names), asset_bands


def is_datacube_compliant(collection: pystac.Collection):
    validation = None
    bands = []
    if len(collection.get_assets()) != 0:
        return False, bands
    for item in collection.get_all_items():
        assets_str, bands = item_assets_info(item)
        item_info = f'{item.bbox}-{item.geometry}-{item.common_metadata.platform}-{assets_str}'
        if validation is None or validation == item_info:
            validation = item_info
        else:
            return True, bands
    return True, bands


def remove_empty_key(dictionary: dict):
    return {k: v for k, v in dictionary.items() if v}
