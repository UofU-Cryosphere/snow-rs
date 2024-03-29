import h5py
import numpy as np
from osgeo import gdal, gdalconst, gdal_array

from snow_rs.lib import ModisGeoTiff

MODIS_MATLAB_FILE = "*{date:%Y%m%d}*.mat"

OUTPUT_FILE = 'WesternUS_{date:%Y%m%d}_{key}'

GDAL_GTIFF = 'GTiff'
GDAL_VRT = 'VRT'
GTIFF_DRIVER = gdal.GetDriverByName(GDAL_GTIFF)
GTIFF_DRIVER_OPTS = [
    "COMPRESS=LZW",
    "TILED=YES",
    "BIGTIFF=IF_SAFER",
    "NUM_THREADS=ALL_CPUS"
]
GTIFF_FILE = OUTPUT_FILE + '.tif'

BAND_DATA_TYPE = gdalconst.GDT_UInt16
BAND_NO_DATA_VALUE = 65535
BAND_NUMBER = 1


def matlab_file(data_dir, date):
    source_file = list(data_dir.glob(MODIS_MATLAB_FILE.format(date=date)))

    if len(source_file) > 0:
        return source_file[0]
    else:
        print(f"WARNING:\n  source file for {date.date()} \n  does not exist.")
        return None


def matlab_to_geotiff(source_dir, output_dir, template_file, date, variable):
    source_file = matlab_file(source_dir, date)

    if source_file is None:
        return None

    file_name = output_dir.joinpath(
        GTIFF_FILE.format(date=date, key=variable)
    ).as_posix()

    geo_tiff = GTIFF_DRIVER.Create(
        file_name,
        template_file.x_size, template_file.y_size,
        BAND_NUMBER, BAND_DATA_TYPE,
        options=GTIFF_DRIVER_OPTS,
    )
    geo_tiff.SetGeoTransform(template_file.geo_transform)
    geo_tiff.SetProjection(ModisGeoTiff.PROJECTION)

    modis_band = geo_tiff.GetRasterBand(BAND_NUMBER)
    modis_band.SetNoDataValue(BAND_NO_DATA_VALUE)

    source_file = h5py.File(source_file.as_posix())
    gdal_array.BandWriteArray(
        modis_band, np.array(source_file[variable]).T
    )

    modis_band.ComputeStatistics(0)
    modis_band.FlushCache()

    del source_file
    del modis_band
    del geo_tiff

    return file_name


def warp_to(file_name, target_srs):
    vrt_file = file_name.replace(
        '.tif', f'_{target_srs.split(":")[1]}.vrt'
    )
    gdal.Warp(
        vrt_file, file_name,
        dstSRS=target_srs, resampleAlg=gdalconst.GRIORA_Bilinear,
        multithread=True, format=GDAL_VRT,
    )
    return vrt_file
