import acquire_zarr as aqz

from pathlib import Path
import numpy as np
import time


class AcquireZarr:
    def __init__(self) -> None:
        base_dir = Path(__file__).parent
        self.__path_to_data = (
            base_dir / "example_data" / "acquire_zarr_data" / "test.zarr"
        ).resolve()

    @property
    def data_path(self) -> str:
        return str(self.__path_to_data)

    def write_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray) -> float:
        settings = aqz.StreamSettings()
        settings.store_path = self.data_path
        settings.compression = aqz.CompressionSettings(
            compressor=aqz.Compressor.BLOSC1,
            codec=aqz.CompressionCodec.BLOSC_LZ4,
            level=1
        )
        settings.data_type=aqz.DataType.UINT8
        settings.dimensions.extend(
            [
                aqz.Dimension(
                    name="t",
                    kind=aqz.DimensionType.TIME,
                    array_size_px=shape[0],
                    chunk_size_px=chunks[0],
                ),
                aqz.Dimension(
                    name="y",
                    kind=aqz.DimensionType.SPACE,
                    array_size_px=shape[1],
                    chunk_size_px=chunks[1],
                ),
                aqz.Dimension(
                    name="x",
                    kind=aqz.DimensionType.SPACE,
                    array_size_px=shape[2],
                    chunk_size_px=chunks[2],
                ),
            ]
        )
        settings.version = aqz.ZarrVersion.V2
        stream = aqz.ZarrStream(settings)

        t = time.perf_counter()
        stream.append(zarr_data)
        total_time = time.perf_counter() - t

        return total_time