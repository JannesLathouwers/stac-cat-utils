import eoepcastac.datacube_utils as datacube_utils

from eoepcastac.stac_generator import EoepcaStacGenerator

if __name__ == '__main__':
    eoepca_stac_gen = EoepcaStacGenerator()

    src_path = 'files'
    catalog = eoepca_stac_gen.create(src_path,
                                     catalog_name='Files Folder Catalog',
                                     collection_paths=['files/logs'],
                                     item_paths=[],
                                     ignore_paths=['files/*.txt'])

    for col in catalog.get_all_collections():
        datacube_utils.make_datacube_compliant(col)

    eoepca_stac_gen.save(dest_path='stac_catalog')
