#!/usr/bin/env python
"""
A couple of model/run combinations are not available on JASMIN and the files are small
enough to download from ESGF and for me to run them at Leeds.

This script can be re-used by modifying the paths to the input data files.

Usage:
    python run_utci.py model scenario run startyear endyear

model: precise name of the model to run (e.g IITM-ESM)
scenario: precise CMIP6-style name of the scenario to run (e.g. ssp585)
run: the realisation of the scenario (i.e. r1i1p1f3)
startyear: the first year to calculate UTCI for (e.g. 2015)
endyear: the last year + 1 (e.g. 2101 to calculate to 2100). Follow pythons `range`
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

model, scenario, run, startyear, endyear = sys.argv[1:6]
print(model, scenario, run)
print()

# data output directory
dataout = "/nfs/b0110/Data/heatstress/%s/%s/%s/" % (model, scenario, run)
mkdir_p(dataout)

# data input directory: this will differ for different models. With iris we can use
# glob
path = "/nfs/b0110/Data/cmip6/%s/%s/%s/3hr/" % (model, scenario, run)

# the final bit of the path will also vary by model grid
vars = ['tas', 'huss', 'ps', 'rlds', 'rlus', 'rsds', 'rsus', 'rsdsdiff', 'uas', 'vas']
cubes = {}
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for var in vars:
        cubes[var] = iris.load(path + '%s/*/%s_3hr_%s_%s_%s_*_*.nc' % (var, var, model, scenario, run))
        equalise_attributes(cubes[var])
        unify_time_units(cubes[var])
        cubes[var] = cubes[var].concatenate_cube()
fp = glob.glob(path + '%s/*/%s_3hr_%s_%s_%s_*_*.nc' % (var, var, model, scenario, run))
grid = fp[0].split('/')[10]

# check that all of the cubes are the same number of time points.
# If they are not, there are some missing variable slices and
# the outputs will not make sense.
# it's sufficient to check everything relative to tas
tas_shape = cubes['tas'].shape[0]
for var in vars:
    if cubes[var].shape[0] != tas_shape:
        raise ValueError(var + ' is a different number of time points to tas.')

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
for year in range(int(startyear), int(endyear)):
    # historical: we want to start in 1985
#    if year < 1985:
#        continue
    # tas timesteps are usually at the end of the period, i.e. 03:00 for 00:00 to 03:00.
    # the first timestep of each year is thus 01 January at 03:00 UTC.
    # it is not clear whether this is an 03:00 instantaneous value or 00:00 to 03:00 mean.
    # hopefully, if it is instantaneous, 3hr data means the biases won't be huge. It also
    # means that the radiation and temperature time steps are in sync.

    # sometimes however this isn't the case. The BCC model has tas timesteps running from
    # 00:00 which are 22:30 to 01:30 means. In BCC the first time step of the year is 
    # 01 January at 00:00 UTC.
    # there's probably a nice iris-friendly way to do this, but for now, just treat BCC
    # as an exception to the usual rule, and be sure to check the filenames and metadata
    # for any new models.
    if model in ['BCC-CSM2-MR', 'MRI-ESM2-0']:
        first_hour_tas=0
    else:
        first_hour_tas=3

    i_start = int(8 * (cftime.date2num(cftime.datetime(year, 1, 1, first_hour_tas, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar) - cftime.date2num(first_time, 'days since 1850-01-01 00:00', calendar=calendar)))
    print(model, scenario, run, year, i_start)
    days_in_year = cftime.date2num(cftime.datetime(year+1, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar) - cftime.date2num(cftime.datetime(year, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar)
    timepoints_in_year = 8 * days_in_year  # 8 x 3-hr timepoints per day
    i_end = i_start + timepoints_in_year
    mjd = np.zeros(timepoints_in_year)
    # radiation timepoints all seem to be 01:30, 04:30, ...
    first_day_of_year = cftime.datetime(year, 1, 1, 1, 30, calendar=calendar)
    for imjd in range(timepoints_in_year):
        mjd[imjd] = modified_julian_date(first_day_of_year + datetime.timedelta(hours=3*imjd))

    # KACE sets diffuse irradiance and upwelling shortwave irradiance at night-time points
    # to missing, rather than zero, which messes up the computation
    rsdsdiff = cubes['rsdsdiff'][i_start:i_end,...].data
    rsus = cubes['rsus'][i_start:i_end,...].data
    if model=='KACE-1-0-G':
        rsdsdiff = rsdsdiff.filled(fill_value = 0)
        rsus = rsus.filled(fill_value = 0)

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
            "rsdsdiff": rsdsdiff,
            "rsus": rsus,
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
            "huss": cubes['huss'][i_start:i_end,...].data,
            "ps": cubes['ps'][i_start:i_end,...].data
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
