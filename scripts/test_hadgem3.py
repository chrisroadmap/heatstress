from climateforcing.utci import utci, mean_radiant_temperature
from climateforcing.solar import cos_mean_solar_zenith_angle, modified_julian_date
import cftime
import datetime
import numpy as np
import iris

import matplotlib.pyplot as pl  # only for testing

# get an array of zenith angles and lit fractions for 2100
mjd = np.zeros(2880)
first_day = cftime.datetime(2100, 1, 1, 1, 30)#, calendar="360_day")
for imjd in range(2880):
    mjd[imjd] = modified_julian_date(first_day + datetime.timedelta(hours=3*imjd))
print(mjd)


tas_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/tas/gn/latest/tas_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010300-210101010000.nc')
huss_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/huss/gn/latest/huss_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010300-210101010000.nc')
rlds_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/rlds/gn/latest/rlds_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010130-210012302230.nc')
rlus_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/rlus/gn/latest/rlus_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010130-210012302230.nc')
rsds_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/rsds/gn/latest/rsds_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010130-210012302230.nc')
rsus_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/rsus/gn/latest/rsus_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010130-210012302230.nc')
rsdsdiff_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/rsdsdiff/gn/latest/rsdsdiff_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010130-210012302230.nc')
uas_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/uas/gn/latest/uas_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010300-210101010000.nc')
vas_cube = iris.load_cube('/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/HadGEM3-GC31-LL/ssp126/r1i1p1f3/3hr/vas/gn/latest/vas_3hr_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_210001010300-210101010000.nc')

lat = tas_cube.coord('latitude').points
lon = tas_cube.coord('longitude').points

lat, lon = np.meshgrid(lat, lon)

mean_cosz, lit = cos_mean_solar_zenith_angle(mjd[0], 3, lat, lon)
pl.contourf(lon, lat, mean_cosz)
pl.show()

mrt = mean_radiant_temperature(
    rlds_cube[0,...].data, 
    rlus_cube[0,...].data, 
    rsdsdiff_cube[0,...].data, 
    rsus_cube[0,...].data, 
    rsds_cube[0,...].data,
    angle_factor_down=0.5,
    angle_factor_up=0.5,
    absorption=0.7,
    emissivity=0.97,
    cos_zenith=mean_cosz.T,
    lit=lit.T
)

pl.contourf(lon, lat, mrt)
pl.colorbar()
pl.show()
