import datetime
import os
from pathlib import Path
from unittest import TestCase

from eoepcastac.stac import EOEPCACollection
from eoepcastac.stac_generator import EoepcaStacGenerator
from eoepcastac.utils import collection_to_assets


class TestCaseConfig(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.stac_generator = EoepcaStacGenerator()
        cls.src_path = os.path.join(os.path.dirname(__file__), './../test_files')
        cls.ignore_paths = [f'{cls.src_path}/products', f'{cls.src_path}/cube']

    @staticmethod
    def remove_output_folder(output_folder):
        for root, dirs, files in os.walk(output_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(output_folder)


class TestEoepcaStacGenerator(TestCaseConfig):

    def test_catalog_creation(self):
        catalog = self.stac_generator.create(self.src_path, ignore_paths=self.ignore_paths)
        collections = list(catalog.get_all_collections())
        self.assertEqual(len(collections), 1, 'Only the generic collection should be created.')
        self.assertEqual(len(collections[0].get_assets()), 7,
                         'Non Rio-Stac supported files should be assets of the generic collection')

        items = list(collections[0].get_items())
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 'test.png', 'Rio-Stac supported files should be generated as STAC Item.')

    def test_simple_collections_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, collection_paths=[f'{self.src_path}/logs'],
                                             ignore_paths=self.ignore_paths)
        collections = list(catalog.get_collections())
        expected_nb_files = {'files': 5, 'logs': 2}
        for collection in collections:
            self.assertEqual(len(collection.assets), expected_nb_files[collection.id])

    def test_glob_collections_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, collection_paths=[f'{self.src_path}/**/*logs'],
                                             ignore_paths=self.ignore_paths)
        catalog_collections = list(catalog.get_collections())
        expected_nb_files = {'files': 5, 'logs': 1, 'extra_logs': 1}
        self.assertEqual(len(catalog_collections), 2)
        self.assertEqual(set(map(lambda col: col.id, catalog_collections)), {'logs', 'files'})

        for collection in catalog_collections:
            self.assertEqual(len(collection.assets), expected_nb_files[collection.id])
            if collection.id == 'extra_logs':
                sub_collections = list(collection.get_collections())
                self.assertEqual(len(sub_collections), 1)
                self.assertEqual(len(sub_collections[0].assets), expected_nb_files[collection.id])

    def test_simple_items_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, item_paths=[f'{self.src_path}/logs'],
                                             ignore_paths=self.ignore_paths)
        items = list(catalog.get_items())
        self.assertEqual(len(items), 1, 'Logs folder should be created as a STAC Item')
        self.assertEqual(items[0].id, 'logs')

    def test_glob_items_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, item_paths=[f'{self.src_path}/**/*logs'],
                                             ignore_paths=self.ignore_paths)
        catalog_items = list(catalog.get_items())
        self.assertEqual(len(catalog_items), 1)
        self.assertEqual(catalog_items[0].id, 'logs')
        self.assertEqual(len(catalog_items[0].assets), 2)

    def test_simple_ignore_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, ignore_paths=[*self.ignore_paths,
                                                                          f'{self.src_path}/logs',
                                                                          Path(f'{self.src_path}/test.png')])
        collections = list(catalog.get_all_collections())
        self.assertEqual(len(collections), 1, 'Only the generic collection should be created.')
        self.assertEqual(len(collections[0].assets), 5)
        items = list(catalog.get_items())
        self.assertEqual(len(items), 0, 'png Item should not be created by Rio-Stac')

    def test_glob_ignore_path_arg(self):
        catalog = self.stac_generator.create(self.src_path, ignore_paths=[*self.ignore_paths,
                                                                          f'{self.src_path}/**/*.log'])
        collections = list(catalog.get_all_collections())
        self.assertEqual(len(collections), 1, 'Only the generic collection should be created.')
        self.assertEqual(len(collections[0].assets), 4, 'log files should be ignored.')

        catalog = self.stac_generator.create(self.src_path, ignore_paths=[*self.ignore_paths,
                                                                          f'{self.src_path}/**/test.*'])
        collections = list(catalog.get_all_collections())
        self.assertEqual(len(collections), 0, 'No generic collection should be created.')

    def test_product_are_recognized(self):
        src_path = os.path.join(self.src_path, 'products')
        catalog = self.stac_generator.create(src_path)
        items = list(catalog.get_items())
        self.assertEqual(len(items), 6, 'Product folders should be created as a STAC Item.')

    def test_asset_href_prefix(self):
        prefix = 'test_prefix'
        catalog = self.stac_generator.create(self.src_path,
                                             collection_paths=[f'{self.src_path}/logs'],
                                             item_paths=[f'{self.src_path}/logs/extra_logs'],
                                             asset_href_prefix=prefix)
        assets = {}
        for collection in catalog.get_all_collections():
            assets = {**assets, **collection_to_assets(collection)}

        for item in catalog.get_all_items():
            assets = {**assets, **item.assets}

        for title, asset in assets.items():
            self.assertTrue(asset.href.startswith(prefix))

    def test_save_catalog(self):
        folder_output = 'test_catalog'
        self.stac_generator.create(self.src_path,
                                   collection_paths=[f'{self.src_path}/logs'],
                                   item_paths=[f'{self.src_path}/logs/extra_logs'])
        self.stac_generator.save(dest_path=folder_output)

        self.assertTrue(os.path.exists(f'{folder_output}/catalog.json'), 'catalog folder should exist')

        self.assertTrue(os.path.exists(f'{folder_output}/files/collection.json'),
                        'generic collection folder should exist')
        self.assertTrue(os.path.exists(f'{folder_output}/files/test.png/test.png.json'),
                        'png item folder and json should exist')

        self.assertTrue(os.path.exists(f'{folder_output}/logs/collection.json'),
                        'logs collection should exist')
        self.assertTrue(os.path.exists(f'{folder_output}/logs/extra_logs/extra_logs.json'),
                        'extra_logs item should exist')

        self.remove_output_folder(folder_output)


class TestDatacubeGeneration(TestCaseConfig):

    def test_datacube_compliant_collection(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        catalog.make_datacube_compliant()
        cube_collection = list(catalog.get_collections())[0]
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('x', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('y', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('time', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('spectral', cube_collection.extra_fields['cube:dimensions'])

    def test_not_datacube_compliant_collection(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/not_cube_collection'],
                                             item_paths=[f'{self.src_path}/cube/not_cube_collection/test.jpg'])
        catalog.make_datacube_compliant()
        cube_collection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:dimensions', cube_collection.extra_fields)

    def test_collection_horizontal_dimension(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        cube_collection: EOEPCACollection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:dimensions', cube_collection.extra_fields)

        extent = [33, 36]
        cube_collection.add_horizontal_dimension('x_axis', axis='x', extent=extent)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('x_axis', cube_collection.extra_fields['cube:dimensions'])
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["x_axis"]["extent"], extent)

    def test_collection_vertical_dimension(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        cube_collection: EOEPCACollection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:dimensions', cube_collection.extra_fields)
        extent = [34, 37]
        cube_collection.add_vertical_dimension('z_axis', extent=extent)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('z_axis', cube_collection.extra_fields['cube:dimensions'])
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["z_axis"]["extent"], extent)

    def test_collection_additional_dimension(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        cube_collection: EOEPCACollection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:dimensions', cube_collection.extra_fields)

        values = ['ex1', 'ex2']
        dim_type = "test"

        cube_collection.add_additional_dimension('extra', type=dim_type , values=values)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('extra', cube_collection.extra_fields['cube:dimensions'])
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["extra"]["type"], dim_type)
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["extra"]["values"], values)

    def test_collection_temporal_dimension(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        cube_collection: EOEPCACollection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:dimensions', cube_collection.extra_fields)

        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=1)

        extent = [start.isoformat(), end.isoformat()]

        cube_collection.add_temporal_dimension('time', extent=extent)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('time', cube_collection.extra_fields['cube:dimensions'])
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["time"]["extent"], extent)

    def test_collection_variable_dimension(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        cube_collection: EOEPCACollection = list(catalog.get_collections())[0]
        self.assertNotIn('cube:variables', cube_collection.extra_fields)

        cube_collection.add_dimension_variable('a_variable', type='data', values=['test', 'test1'])
        self.assertIn('cube:variables', cube_collection.extra_fields)
        self.assertIn('a_variable', cube_collection.extra_fields['cube:variables'])

    def test_overwrite_temporal_dimension_in_datacube_compliant_collection(self):
        catalog = self.stac_generator.create(f'{self.src_path}/cube',
                                             collection_paths=[f'{self.src_path}/cube/cube_collection'])
        catalog.make_datacube_compliant()
        cube_collection = list(catalog.get_collections())[0]
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('x', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('y', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('time', cube_collection.extra_fields['cube:dimensions'])
        self.assertIn('spectral', cube_collection.extra_fields['cube:dimensions'])

        # new extent for this test
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=1)
        extent = [start.isoformat(), end.isoformat()]

        # Try to add without replace
        cube_collection.add_temporal_dimension('time', extent=extent, replace=False)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('time', cube_collection.extra_fields['cube:dimensions'])
        # Verify that the dimension has not been updated
        self.assertNotEqual(cube_collection.extra_fields["cube:dimensions"]["time"]["extent"], extent)

        # Add with replace
        cube_collection.add_temporal_dimension('time', extent=extent, replace=True)
        self.assertIn('cube:dimensions', cube_collection.extra_fields)
        self.assertIn('time', cube_collection.extra_fields['cube:dimensions'])
        # Verify that the dimension was replaced
        self.assertEqual(cube_collection.extra_fields["cube:dimensions"]["time"]["extent"], extent)

    def test_save_datacube_compliant_collection(self):
        folder_output = 'test_catalog'
        catalog  = self.stac_generator.create(self.src_path,
                                   collection_paths=[f'{self.src_path}/logs'],
                                   item_paths=[f'{self.src_path}/logs/extra_logs'])

        catalog.make_datacube_compliant()
        self.stac_generator.save(dest_path=folder_output)
        self.assertTrue(os.path.exists(f'{folder_output}/catalog.json'), 'catalog folder should exist')

        self.assertTrue(os.path.exists(f'{folder_output}/files/collection.json'),
                        'generic collection folder should exist')
        self.assertTrue(os.path.exists(f'{folder_output}/files/test.png/test.png.json'),
                        'png item folder and json should exist')

        self.assertTrue(os.path.exists(f'{folder_output}/logs/collection.json'),
                        'logs collection should exist')
        self.assertTrue(os.path.exists(f'{folder_output}/logs/extra_logs/extra_logs.json'),
                        'extra_logs item should exist')
        self.remove_output_folder(folder_output)