#!/usr/bin/env python

"""
This script calculates the bias-corrected exceedence probabilities for each model

1.  For the following thresholds:
    a. 26C
    b. 32C
    c. 38C
    d. 46C
    calculate the proportion of time each grid cell in ERA5 exceeds this level of UTCI.

2.  Taking the percentiles from 1a-d, calculate the UTCI in the 1985-2014 climate 
    in each CMIP6 model that corresponds to this threshold. This is a form of bias
    correction.

3.  Apply these thresholds forward to the future scenario.
"""

import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import iris.analysis.cartography
import iris.coord_categorisation
import matplotlib.pyplot as pl
from climateforcing.utils import mkdir_p
import numpy as np
import scipy.stats as st
import sys

# Part 1
era5dir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg/'
cube_era5 = iris.load(era5dir + '*.nc')
equalise_attributes(cube_era5)
unify_time_units(cube_era5)
cube_era5 = cube_era5.concatenate_cube()

outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg_exceedence/' 
mkdir_p(outdir)

result26 = cube_era5.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+26)
iris.save(result26, outdir + 'ECMWF_utci_v1.0_con_gt_26.nc')
result32 = cube_era5.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+32)
iris.save(result32, outdir + 'ECMWF_utci_v1.0_con_gt_32.nc')
result38 = cube_era5.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+38)
iris.save(result38, outdir + 'ECMWF_utci_v1.0_con_gt_38.nc')
result46 = cube_era5.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+46)
iris.save(result46, outdir + 'ECMWF_utci_v1.0_con_gt_46.nc')
