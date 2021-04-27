"""
This script is designed to run on the LOTUS cluster on JASMIN.

It will calculate UTCI from the HadGEM3-GC31-LL model for historical and SSP5-8.5 for
the year 2100. It should in theory be applicable this to other models and years, though
caution is needed to make the calendar correct.

For now it saves to /scratch (we need a group workspace for this work)
"""

from climateforcing.utci import universal_thermal_climate_index, mean_radiant_temperature
from climateforcing.solar import cos_mean_solar_zenith_angle, modified_julian_date
import cftime
import datetime
import numpy as np
import iris
import matplotlib.pyplot as pl
import warnings

# data output directory: need a GWS!
dataout = "/work/scratch-nopw/pmcjs/"

# data input directory: this will differ for different models
path = "/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp585/r1i1p1f3/3hr/"

# get an array of zenith angles and lit fractions for 2100
# 2880 is number of 3-hour periods in a 360-day year. This will depend on the model
# year length
ntime = 2880
mjd = np.zeros(ntime)
first_day = cftime.datetime(2100, 1, 1, 1, 30, calendar="360_day")
for imjd in range(ntime):
    mjd[imjd] = modified_julian_date(first_day + datetime.timedelta(hours=3*imjd))

# the final bit of the path will also vary by model and needs to be generalised
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    tas_cube = iris.load_cube(path + 'tas/gn/latest/tas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
    huss_cube = iris.load_cube(path + 'huss/gn/latest/huss_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
    rlds_cube = iris.load_cube(path + 'rlds/gn/latest/rlds_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
    rlus_cube = iris.load_cube(path + 'rlus/gn/latest/rlus_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
    rsds_cube = iris.load_cube(path + 'rsds/gn/latest/rsds_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
    rsus_cube = iris.load_cube(path + 'rsus/gn/latest/rsus_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
    rsdsdiff_cube = iris.load_cube(path + 'rsdsdiff/gn/latest/rsdsdiff_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010130-210012302230.nc')
    uas_cube = iris.load_cube(path + 'uas/gn/latest/uas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
    vas_cube = iris.load_cube(path + 'vas/gn/latest/vas_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')

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
