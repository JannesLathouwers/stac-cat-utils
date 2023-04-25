import os
from glob import glob
from pathlib import Path

import pystac

from lxml import etree


def is_product_folder(path):
    folder_name = os.path.basename(path)
    folder_content = os.listdir(path)

    if folder_name.startswith('S1') and 'manifest.safe' in folder_content:
        tree = etree.parse(os.path.join(path, 'manifest.safe'))
        elements = tree.findall('.//s1sarl1:productType', tree.getroot().nsmap)
        if len(elements) > 0 and elements[0].text == 'GRD':
            return True, 'S1', 'GRD'
        if len(elements) > 0 and elements[0].text == 'SLC':
            return True, 'S1', 'SLC'

    if folder_name.startswith('S2') and 'manifest.safe' in folder_content:
        tree = etree.parse(os.path.join(path, 'manifest.safe'))
        elements = tree.findall(".//*[@unitType='Product_Level-2A']")
        if len(elements) > 0:
            return True, 'S2', 'L2A'
        elements = tree.findall(".//*[@unitType='Product_Level-1C']")
        if len(elements) > 0:
            return True, 'S2', 'L1C'

    for file in folder_content:
        if os.path.isfile(os.path.join(path, file)) and file.lower().endswith('mtl.xml'):
            return True, 'LANDSAT', file

    return False, None, None


def is_collection_empty(collection: pystac.Collection):
    return not(
        list(collection.get_all_items()) or collection.get_assets().keys() or list(collection.get_all_collections())
    )


def convert_paths(path_list: list):
    matches = []
    for path in path_list:
        if isinstance(path, Path):
            matches.extend(glob(str(path), recursive=True))
        else:
            matches.extend(glob(path, recursive=True))
    return matches
