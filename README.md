# EOEPCA STAC Catalogue Utilities

EOEPCA STAC Catalogue Utilities is a library that provides utility functions implemented in the Python 3 scripting 
language that facilitate the generation of STAC files from existing files and folders.

## Installation
### Install from PyPi (recommended)

```shell
pip install eoepcastac
```

### Install from source
```shell
git clone https://github.com/orgs/SpaceApplications/teams/eos-team
cd stac-cat-utils
pip install .
```

## Documentation
See the documentation page for the latest docs.

## Usage

### STAC Generator

The generation of the STAC files, for existing files and folders, is handled by the `EoepcaStacGenerator` class:
```python
from eoepcastac.stac_generator import EoepcaStacGenerator
stac_generator = EoepcaStacGenerator()
```

Concrete generation of STAC files is handled by the `create` and `save` method of the `EoepcaStacGenerator` generator:

1. `create`: Return an STAC EOEPCACatalog object (pystac.Catalog augmented with additional features) for the given source path.
     * `src_path`: (Required) Root path of the folder.
     * `catalog_name`: (Optional) Name of the catalogue. Default: "Catalogue".
     * `collection_paths`: (Optional) List of paths that must be considered as collections. Array of strings, globs and Path instances. Default: None.
     * `item_paths`: (Optional) List of paths that must be considered as items. Array of strings, globs and Path instances. Default: None.
     * `ignore_paths`: (Optional) List of paths to ignore. Array of strings, globs and Path instances. Default: None.
     * `asset_href_prefix`: (Optional) prefix to append to all assets href. Default: '/'.
   ```python
   from eoepcastac.stac_generator import EoepcaStacGenerator
   stac_generator = EoepcaStacGenerator()
   catalog = stac_generator.create('.')
   ```

2. `save`: Saves the generated STAC EOEPCACatalog object to a destination path.
     * `dest_path`: (Optional) Destination path where the STAC catalog is saved. Default: 'stac_<catalog_name>' .
     * `asset_href_prefix`: (Optional) prefix to append to all assets href. Default: '/'.
    ```python
    from eoepcastac.stac_generator import EoepcaStacGenerator
    stac_generator = EoepcaStacGenerator()
    catalog = stac_generator.create('.')
    stac_generator.save()
    ```
### Datacube
The catalog and collection created during the generation process are augmented with methods to support the [Datacube Extension Specification
](https://github.com/stac-extensions/datacube).

The following methods are available for:
1. `EOEPCACatalog`:
   * `make_cube_compliant`: make all collection of the catalog datacube compliant if possible
      ```python
      from eoepcastac.stac_generator import EoepcaStacGenerator
      stac_generator = EoepcaStacGenerator()
      catalog = stac_generator.create('.')
      catalog.make_datacube_compliant()
      ```

2. `EOEPCACollection`:
   * `make_datacube_compliant`: make the collection datacube compliant if possible
   * `add_horizontal_dimension`: add a [Horizontal Dimension](https://github.com/stac-extensions/datacube#horizontal-spatial-raster-dimension-object) to the collection
   * `add_vertical_dimension`: add a [Vertical Dimension](https://github.com/stac-extensions/datacube#vertical-spatial-dimension-object) to the collection
   * `add_temporal_dimension`: add a [Temporal Dimension](https://github.com/stac-extensions/datacube#temporal-dimension-object) to the collection
   * `add_additional_dimension`: add a [Custom Dimension](https://github.com/stac-extensions/datacube#additional-dimension-object) to the collection
   * `add_dimension_variable`: add a [Dimension Variable](https://github.com/stac-extensions/datacube#variable-object) to the collection
      ```python
      from eoepcastac.stac_generator import EoepcaStacGenerator
      stac_generator = EoepcaStacGenerator()
      catalog = stac_generator.create('.')
     
      for collection in catalog.get_all_collections():
          # Collection Dimension example
          collection.make_datacube_compliant()
          collection.add_horizontal_dimension(...)
          collection.add_vertical_dimension(...)
          collection.add_temporal_dimension(...)
          collection.add_additional_dimension(...)
          collection.add_dimension_variable(...)
      ```

## Examples
Python script showcasing the usage of the library are available in under the `examples` folder.
