import logging
import os
import re
import pystac

from glob import glob
from lxml import etree

logger = logging.getLogger("EoepcaStacGenerator")
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
        elements = tree.findall(".//*[@unitType='Product_Level-2A']")
        if len(elements) > 0:
            return {'is_product': True, 'name': 'S2', 'extra_info': 'L2A'}
        elements = tree.findall(".//*[@unitType='Product_Level-1C']")
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
            matches.extend(glob(str(path), recursive=True))
    return matches


def collection_to_assets(collection: pystac.Collection):
    all_assets = collection.assets
    for col in collection.get_all_collections():
        all_assets = {**all_assets, **collection_to_assets(col)}
    for item in collection.get_all_items():
        all_assets = {**all_assets, **item.assets}
    return all_assets
