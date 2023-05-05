import pystac

from eoepcastac.stac_generator import EoepcaStacGenerator

if __name__ == '__main__':
    eoepca_stac_gen = EoepcaStacGenerator()

    src_path = './../test_files'
    catalog = eoepca_stac_gen.create(src_path,
                                     collection_paths=[f'{src_path}/logs'],
                                     item_paths=[f'{src_path}/logs/extra_logs'],
                                     ignore_paths=[f'{src_path}/cube'])

    # Returned catalog is a pystac.Catalog which can be modified using the pystac library API
    catalog.title = 'new title'
    catalog.normalize_hrefs('test')

    # Catalog collection can be set to be datacube compliant if possible, please be aware that this is a custom
    # method provided by EOEPCACatalog which inherits from pystac.Catalog
    catalog.make_datacube_compliant()

    # Using the pystac.Catalog save method
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
