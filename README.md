# Snow-RS (Remote Sensing) utilities

Python package with tools for processing snow property information from
remote sensing sources.

## Setup conda environment

Use the supplied `environment.yml` file to set up a Python environment with
conda to run or develop utilities.

```shell
conda env create -f environment.yml
```

### Installation for execution

```shell
git clone git@github.com:UofU-Cryosphere/snow-rs.git
cd snow-rs
python -m pip install .
```

### Installation for execution & development

```shell
git clone git@github.com:UofU-Cryosphere/snow-rs.git
cd snow-rs
python -m pip install -e .
```

### Technical note

Uses Dask to parallelize extraction on daily basis.

# Current Tools

## MODIS

Contains a converter utility to extract MODIS gap-filled values for a
given variable. The source files are expected to as unprojected Matlab files.

### Sample call:

```shell
variable_from_modis --source-dir /data/MODIS_files \ 
                    --output-dir /your/output/dir \
                    --year 2018 \
                    ---year-format water \
                    --t-srs EPSG:4326 \
                    --variable albedo_observed_muZ
```

### Data required

The package data dir includes
the [WesternUS.tif](src/snow_rs/data/modis/README.md)
template file used to create the projected GeoTiff results.
It is installed automatically with the package.
