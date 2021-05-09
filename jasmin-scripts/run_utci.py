#!/usr/bin/env python
"""
This script is designed to run on the LOTUS cluster on JASMIN.

It will calculate UTCI from a specified model and under a specified scenario passed
on the command line.

For now it saves to /scratch (we need a group workspace for this work)

Usage:
    python run_generic.py index

index is an integer that provides the model, scenario and run to use and is a lookup to
a csv file.

model: precise name of the model to run (e.g IITM-ESM)
scenario: precise CMIP6-style name of the scenario to run (e.g. ssp585)
run: the realisation of the scenario (i.e. r1i1p1f3)
"""

from climateforcing.utci import universal_thermal_climate_index, mean_radiant_temperature
from climateforcing.solar import cos_mean_solar_zenith_angle, modified_julian_date
from climateforcing.utils import mkdir_p
import cftime
import datetime
import numpy as np
import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import matplotlib.pyplot as pl
import pandas as pd
import warnings
import sys
import glob

index = sys.argv[1]
df = pd.read_csv('../data/3hr_models.csv', index_col=0)
model, scenario, run = df.loc[int(index)]

# data output directory: need a GWS!
dataout = "/work/scratch-nopw/pmcjs/%s/%s/%s/" % (model, scenario, run)
mkdir_p(dataout)

# data input directory: this will differ for different models. With iris we can use
# glob
path = "/badc/cmip6/data/CMIP6/*/*/%s/%s/%s/3hr/" % (model, scenario, run)

# the final bit of the path will also vary by model and needs to be generalised
vars = ['tas', 'huss', 'rlds', 'rlus', 'rsds', 'rsus', 'rsdsdiff', 'uas', 'vas']
cubes = {}
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for var in vars:
        cubes[var] = iris.load(path + '%s/*/latest/%s_3hr_%s_%s_%s_*_*.nc' % (var, var, model, scenario, run))
        equalise_attributes(cubes[var])
        unify_time_units(cubes[var])
        cubes[var] = cubes[var].concatenate_cube()
fp = glob.glob(path + '%s/*/latest/%s_3hr_%s_%s_%s_*_*.nc' % (var, var, model, scenario, run))
grid = fp[0].split('/')[12]

# get lat and lon
lat = cubes['tas'].coord('latitude').points
lon = cubes['tas'].coord('longitude').points
lonmesh, latmesh = np.meshgrid(lon, lat)

nlat = len(lat)
nlon = len(lon)

# sort out times
all_time_coord = cubes['tas'].coord('time')
all_time_points = all_time_coord.units.num2date(all_time_coord.points)
n_all_time = len(all_time_points)
calendar = all_time_coord.units.calendar
first_time = all_time_points[0]
last_time = all_time_points[-1]

# start the year chunking loop
for year in range(first_time.year, last_time.year+1):
    # historical: we want to start in 1985
    if year < 1985:
        continue
    # tas timesteps I think are at the end of the period, i.e. 03:00 for 00:00 to 03:00 mean
    # radiation timesteps should be at the centre: 01:30 for 00:00 to 03:00 mean
    i_start = int(8 * (cftime.date2num(cftime.datetime(year, 1, 1, 3, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar) - cftime.date2num(first_time, 'days since 1850-01-01 00:00', calendar=calendar)))
    print(model, scenario, run, year, i_start)
    days_in_year = cftime.date2num(cftime.datetime(year+1, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar) - cftime.date2num(cftime.datetime(year, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar)
    timepoints_in_year = 8 * days_in_year  # 8 x 3-hr timepoints per day
    i_end = i_start + timepoints_in_year
    mjd = np.zeros(timepoints_in_year)
    first_day_of_year = cftime.datetime(year, 1, 1, 1, 30, calendar=calendar)
    for imjd in range(timepoints_in_year):
        mjd[imjd] = modified_julian_date(first_day_of_year + datetime.timedelta(hours=3*imjd))

    # calculate 3hr-mean solar zenith
    mean_cosz = np.ones((timepoints_in_year, nlat, nlon)) * np.nan
    lit = np.ones((timepoints_in_year, nlat, nlon)) * np.nan
    for i in range(timepoints_in_year):
        mean_cosz[i, ...], lit[i, ...] = cos_mean_solar_zenith_angle(mjd[i], 3, lat, lon)

    # calculate mean radiant temperature
    mrt = mean_radiant_temperature(
        {
            "rlds": cubes['rlds'][i_start:i_end,...].data,
            "rlus": cubes['rlus'][i_start:i_end,...].data,
            "rsdsdiff": cubes['rsdsdiff'][i_start:i_end,...].data,
            "rsus": cubes['rsus'][i_start:i_end,...].data,
            "rsds": cubes['rsds'][i_start:i_end,...].data,
        },
        angle_factor_down=0.5,
        angle_factor_up=0.5,
        absorption=0.7,
        emissivity=0.97,
        cos_zenith=mean_cosz,
        lit=lit
    ) 

    # regrid wind to temperature grid
    # don't think area-weighting makes sense, use bi-linear
    uas_cube_regrid = cubes['uas'][i_start:i_end,...].regrid(cubes['tas'], iris.analysis.Linear())
    vas_cube_regrid = cubes['vas'][i_start:i_end,...].regrid(cubes['tas'], iris.analysis.Linear())
    wind = np.sqrt(uas_cube_regrid.data**2 + vas_cube_regrid.data**2)

    # calculate UTCI
    utci = universal_thermal_climate_index(
        {
            "tas": cubes['tas'][i_start:i_end,...].data,
            "sfcWind": wind,
            "huss": cubes['huss'][i_start:i_end,...].data
        },
        mrt
    )

    # make cubes out of output (only UTCI to save space and time)
    utci_cube = iris.cube.Cube(
        utci,
        units='K',
        var_name='utci',
        long_name='Universal Thermal Climate Index',
        dim_coords_and_dims=[
            (cubes['tas'][i_start:i_end,...].coord('time'), 0),
            (cubes['tas'][i_start:i_end,...].coord('latitude'), 1),
            (cubes['tas'][i_start:i_end,...].coord('longitude'), 2)
        ]
    )
    #mrt_cube = iris.cube.Cube(
    #    mrt,
    #    units='K',
    #    var_name='mrt',
    #    long_name='Mean Radiant Temperature',
    #    dim_coords_and_dims=[
    #        (tas_cube.coord('time'), 0),
    #        (tas_cube.coord('latitude'), 1),
    #        (tas_cube.coord('longitude'), 2)
    #    ]
    #)

    # save the output
    iris.save(utci_cube, dataout + 'utci_3hr_%s_%s_%s_%s_%4d01010300-%d01010000.nc' % (model, scenario, run, grid, year, year+1))
