"""
This script is designed to run on the LOTUS cluster on JASMIN.

It will calculate UTCI from a specified model and under a specified scenario passed
on the command line.

For now it saves to /scratch (we need a group workspace for this work)

Usage:
    python run_generic.py model scenario run

model: precise name of the model to run (e.g HadGEM3-GC31-LL)
scenario: precise CMIP6-style name of the scenario to run (e.g. ssp585)
run: the realisation of the scenario (i.e. r1i1p1f3)
"""

from climateforcing.utci import universal_thermal_climate_index, mean_radiant_temperature
from climateforcing.solar import cos_mean_solar_zenith_angle, modified_julian_date
import cftime
import datetime
import numpy as np
import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import matplotlib.pyplot as pl
import warnings
import sys

model, scenario, run = (sys.argv[1], sys.argv[2], sys.argv[3])

# data output directory: need a GWS!
dataout = "/work/scratch-nopw/pmcjs/"

# data input directory: this will differ for different models. With iris we can use
# glob
path = "/badc/cmip6/data/CMIP6/*/*/%s/%s/%s/3hr/" % (model, scenario, run)

# the final bit of the path will also vary by model and needs to be generalised
#vars = ['tas', 'huss', 'rlds', 'rlus', 'rsds', 'rsus', 'rsdsdiff', 'uas', 'vas']
vars = ['tas']
cubes = {}
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for var in vars:
        cubes[var] = iris.load(path + 'tas/*/latest/%s_3hr_%s_%s_%s_*_*.nc' % (var, model, scenario, run))
        equalise_attributes(cubes[var])
        unify_time_units(cubes[var])
        cubes[var] = cubes[var].concatenate_cube()
#    tas_cube = iris.load(path + 'tas/*/latest/tas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
#    huss_cube = iris.load(path + 'huss/*/latest/huss_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
#    rlds_cube = iris.load(path + 'rlds/*/latest/rlds_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
#    rlus_cube = iris.load(path + 'rlus/*/latest/rlus_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
#    rsds_cube = iris.load(path + 'rsds/*/latest/rsds_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
#    rsus_cube = iris.load(path + 'rsus/*/latest/rsus_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
#    rsdsdiff_cube = iris.load(path + 'rsdsdiff/*/latest/rsdsdiff_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
#    uas_cube = iris.load(path + 'uas/*/latest/uas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
#    vas_cube = iris.load(path + 'vas/*/latest/vas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')


# get an array of zenith angles and lit fractions for 2100
# TODO: we want to break into one-year chunks and loop, to prevent memory issues
time = cubes['tas'].coord('time')
times = time.units.num2date(time.points)
ntime = len(times)
calendar = time.units.calendar
first_time = times[0]
last_time = times[-1]
print(first_time.year, last_time.year)
for year in range(first_time.year, last_time.year):
    print(year, cftime.date2num(cftime.datetime(year+1, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar) - cftime.date2num(cftime.datetime(year, 1, 1, 0, 0, 0, calendar=calendar), 'days since 1850-01-01 00:00', calendar=calendar))
#mjd = np.zeros(ntime)
#first_day = cftime.datetime(first_time.year, first_time.month, first_time.day, 1, 30, calendar=calendar)
#print(ntime, calendar, first_day)
#for imjd in range(ntime):
#    mjd[imjd] = modified_julian_date(first_day + datetime.timedelta(hours=3*imjd))
#print(mjd)
sys.exit()

lat = tas_cube.coord('latitude').points
lon = tas_cube.coord('longitude').points
lonmesh, latmesh = np.meshgrid(lon, lat)

nlat = len(lat)
nlon = len(lon)

# calculate 3hr-mean solar zenith
mean_cosz = np.ones((ntime, nlat, nlon)) * np.nan
lit = np.ones((ntime, nlat, nlon)) * np.nan
for i in range(ntime):
    mean_cosz[i, ...], lit[i, ...] = cos_mean_solar_zenith_angle(mjd[i], 3, lat, lon)

# calculate mean radiant temperature
mrt = mean_radiant_temperature(
    {
        "rlds": rlds_cube.data,
        "rlus": rlus_cube.data,
        "rsdsdiff": rsdsdiff_cube.data,
        "rsus": rsus_cube.data,
        "rsds": rsds_cube.data,
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
uas_cube_regrid = uas_cube.regrid(tas_cube, iris.analysis.Linear())
vas_cube_regrid = vas_cube.regrid(tas_cube, iris.analysis.Linear())
wind = np.sqrt(uas_cube_regrid.data**2 + vas_cube_regrid.data**2)

# calculate UTCI
utci = universal_thermal_climate_index(
    {
        "tas": tas_cube.data,
        "sfcWind": wind,
        "huss": huss_cube.data
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
        (tas_cube.coord('time'), 0),
        (tas_cube.coord('latitude'), 1),
        (tas_cube.coord('longitude'), 2)
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

# save the output - should automate by model name etc
iris.save(utci_cube, dataout + 'utci_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
