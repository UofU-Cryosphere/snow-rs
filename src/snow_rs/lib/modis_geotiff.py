from dataclasses import dataclass, field
from importlib.resources import files

from osgeo import gdal, gdalconst


@dataclass
class ModisGeoTiff:
    x_size: int = field(init=False)
    y_size: int = field(init=False)
    geo_transform: tuple = field(init=False)

    PROJECTION = '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 ' \
                 '+a=6371007.181 +b=6371007.181 +units=m ' \
                 '+no_defs +nadgrids=@null +wktext'

    WESTERN_US_TEMPLATE = 'WesternUS.tif'

    def __post_init__(self):
        self.__load_template_data()

    def __load_template_data(self):
        template = gdal.Open(
            files('snow_rs').joinpath(
                f'data/modis/{self.WESTERN_US_TEMPLATE}'
            ).as_posix(),
            gdalconst.GA_ReadOnly
        )

        self.x_size = template.RasterXSize
        self.y_size = template.RasterYSize
        self.geo_transform = template.GetGeoTransform()

        del template
