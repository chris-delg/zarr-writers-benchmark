import tensorstore as ts
import time
import numpy as np


def create_zarr(folder_path: str, zarr_spec: dict, zarr_data: np.ndarray) -> None:
    zarr_spec['kvstore']['path'] = folder_path
    t = time.perf_counter()
    zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
    zarr_create[...].write(zarr_data).result()
    print(f"TensorStore -> creating zarr : {time.perf_counter() - t} seconds")


def copy_zarr(source_path: str, result_path: str) -> None:
    # copying data from source 
    zarr_store = ts.open(
        {
            'driver': 'zarr',
            'kvstore': {
                'driver': 'file',
                'path': source_path
            }
        },
        open=True
    ).result()
    zarr_data = zarr_store.read().result().copy()
    zarr_spec = zarr_store.spec().to_json()
    
    # writing data to the new folder
    create_zarr(result_path, zarr_spec=zarr_spec, zarr_data=zarr_data)


# Use this as a template if needed for zarr_specs     
'''
zarr_spec = {
    'driver': 'zarr',
    'dtype': 'uint8',
    'kvstore': {
        'driver': 'file',
        'path': 'your path here',
    },
    'metadata': {
        'chunks': [64, 540, 960],
        'compressor': None,
        'dimension_separator': '/',
        'dtype': '|u1',
        'fill_value': 0,
        'filters': None,
        'order': 'C',
        'shape': [64, 1080, 1920],
        'zarr_format': 2,
    },
    'transform': {
        'input_exclusive_max': [[64], [1080], [1920]],
        'input_inclusive_min': [0, 0, 0],
    },
}
'''        