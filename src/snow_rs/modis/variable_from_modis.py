import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple

import dask
import numpy as np

from snow_rs.lib import ModisGeoTiff
from snow_rs.lib.command_line_helpers import add_dask_options
from snow_rs.lib.dask_utils import run_with_client
from snow_rs.modis.matlab_to_geotiff import matlab_to_geotiff, warp_to

ONE_DAY = timedelta(days=1)


class ConversionConfig(NamedTuple):
    variable: str
    source_dir: Path
    output_dir: Path
    year_format: str
    year: int
    modis_us: ModisGeoTiff
    target_srs: str


def argument_parser():
    parser = argparse.ArgumentParser(
        description='Convert matlab files to a GeoTiff',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '--source-dir',
        required=True,
        type=Path,
        help='Base directory. The files to convert are expected to be in a '
             'folder with the year. Example: 2018'
             '\n'
    )

    parser.add_argument(
        '--output-dir',
        required=True,
        type=Path,
        help='Output directory. Where coverted files are saved.'
             '\n'
    )

    parser.add_argument(
        '--year-format',
        required=True,
        type=str,
        choices=['calendar', 'water'],
        help='Choose formating of input direcetory. Determines the formatting '
             'of the date range to process.'
             '\n'
    )

    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='Determines the date range to process'
    )
    
    parser.add_argument(
        '--variable',
        required=True,
        type=str,
        help='Variable to extract from the matlab files'
    )
    
    parser.add_argument(
        '--t-srs',
        type=str,
        help='When given, creates a GDAL-VRT file with that reference system.'
             ' Example: EPSG:4326'
    )

    parser = add_dask_options(parser)
    
    return parser


def config_for_arguments(arguments):
    return ConversionConfig(
        variable=arguments.variable,
        source_dir=arguments.source_dir / str(arguments.year),
        output_dir=arguments.output_dir,
        year_format=arguments.year_format,
        year=arguments.year,
        modis_us=ModisGeoTiff(),
        target_srs=arguments.t_srs,
    )


def date_range(year, date_format):
    if date_format == 'calendar':
        # use standard calendar date format
        d0 = datetime(year, 1, 1)
        d1 = datetime(year + 1, 1, 1)  
    elif date_format == 'water':
        # use water-year formatting
        d0 = datetime(year - 1, 9, 30)
        d1 = datetime(year, 10, 1)
        
    return np.arange(d0, d1, ONE_DAY).astype(datetime)


@dask.delayed
def write_date(date, config):
    file = matlab_to_geotiff(
        config.source_dir,
        config.output_dir,
        config.modis_us,
        date,
        config.variable,
    )

    if file is not None and config.target_srs:
        warp_to(file, config.target_srs)


def main():
    arguments = argument_parser().parse_args()

    if not arguments.source_dir.exists():
        raise IOError(
            f'Given source folder does not exist: {arguments.source_dir}'
        )

    if not arguments.output_dir.exists():
        raise IOError(
            f'Given output folder does not exist: {arguments.output_dir}'
        )

    with run_with_client(arguments.cores, arguments.memory):
        config = config_for_arguments(arguments)
        files = [
            write_date(date, config)
            for date in date_range(arguments.year, arguments.year_format)
        ]
        dask.compute(files)


if __name__ == '__main__':
    main()
