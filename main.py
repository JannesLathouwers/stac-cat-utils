from eoepca_stac.stac import EoepcaStacGenerator
from pathlib import Path

if __name__ == '__main__':
    eoepca_stac_gen = EoepcaStacGenerator()

    path_instance = Path('examples/files/test.txt')
    ignore_paths = ['examples/files/logs', path_instance, '**/*.SAFE']

    src_path = 'examples/files'
    eoepca_stac_gen.create(src_path,
                           catalog_name='Files Folder Catalog',
                           collection_paths=[],
                           item_paths=[],
                           ignore_paths=ignore_paths)

    eoepca_stac_gen.save(dest_path='stac_catalog')
