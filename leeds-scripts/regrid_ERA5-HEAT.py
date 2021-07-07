#!/usr/bin/env python
# coding: utf-8

# # Regrid the ERA5-HEAT data
# 
# Note: the ERA5-HEAT data are not on JASMIN, so this is a "run at Leeds" script. 
# 
# This notebook processes the 1/4 degree ERA5-HEAT dataset from 1985 to 2014, on to a 1 degree grid. This dataset size is more manageable for bias-correction than the original 1/4 degree, and is still finer than the resolution of most climate models.
# 
# The regridded ERA5-HEAT data will then be uploaded to the GWS.


import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import iris.analysis.cartography
import iris.coord_categorisation
import numpy as np
from tqdm import tqdm
import glob


# ## Make a dummy grid
# 
# iris needs something to regrid to: we have to make it from scratch because we're not importing the 1 degree grid from a model.


latitude = iris.coords.DimCoord(
    np.arange(-89.5,90,1),
    standard_name='latitude',
    units='degrees',
    long_name='Latitude',
    var_name='lat',
    coord_system=None
)
longitude = iris.coords.DimCoord(
    np.arange(-179.5,180,1),
    standard_name='longitude',
    long_name='Longitude',
    var_name='lon',
    units='degrees',
    circular=True,
    coord_system=None
)

ny = len(latitude.points)
nx = len(longitude.points)

dummy_data = np.zeros((ny, nx))
dummy_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
dummy_cube.coord('longitude').guess_bounds()
dummy_cube.coord('latitude').guess_bounds()


# ## Do the regrid and save output


era5heatdir = '/nfs/b0110/Data/ERA5-HEAT/original/'
regriddir = '/nfs/b0110/Data/ERA5-HEAT/regrid_1deg/'

filelist = glob.glob('/nfs/b0110/Data/ERA5-HEAT/original/*.nc')
for file in tqdm(filelist):
    pass



first_file = True
for file in tqdm(filelist):
    cube_era5 = iris.load_cube(file)
    filename = file.split('/')[-1]
    cube_era5.coord('longitude').guess_bounds()
    cube_era5.coord('latitude').guess_bounds()

    # regrid the ERA5 to the new grid
    if first_file:
        regridder = iris.analysis.AreaWeighted().regridder(cube_era5, dummy_cube)
        first_file = False
    cube_era5_regrid = regridder(cube_era5)

    # save the output
    iris.save(cube_era5_regrid, regriddir + filename)



