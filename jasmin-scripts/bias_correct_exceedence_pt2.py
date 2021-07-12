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

scenarios = {}
scenarios['ACCESS-CM2'] = {}
scenarios['ACCESS-CM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['CanESM5'] = {}
scenarios['CanESM5']['r1i1p2f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['CMCC-CM2-SR5'] = {}
scenarios['CMCC-CM2-SR5']['r1i1p1f1'] = ['historical', 'ssp245', 'ssp585']
scenarios['MRI-ESM2-0'] = {}
scenarios['MRI-ESM2-0']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['KACE-1-0-G'] = {}
scenarios['KACE-1-0-G']['r1i1p1f1'] = ['historical', 'ssp245']
scenarios['HadGEM3-GC31-MM'] = {}
scenarios['HadGEM3-GC31-MM']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp585']
scenarios['HadGEM3-GC31-LL'] = {}
scenarios['HadGEM3-GC31-LL']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['BCC-CSM2-MR'] = {}
scenarios['BCC-CSM2-MR']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['CMCC-ESM2'] = {}
scenarios['CMCC-ESM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']


# Part 1
era5dir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg/'
cube_era5 = iris.load(era5dir + '*.nc')
equalise_attributes(cube_era5)
unify_time_units(cube_era5)
cube_era5 = cube_era5.concatenate_cube()

indir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg_exceedence/' 
result26 = iris.load_cube(indir + 'ECMWF_utci_v1.0_con_gt_26.nc')
result32 = iris.load_cube(indir + 'ECMWF_utci_v1.0_con_gt_32.nc')
result38 = iris.load_cube(indir + 'ECMWF_utci_v1.0_con_gt_38.nc')
result46 = iris.load_cube(indir + 'ECMWF_utci_v1.0_con_gt_46.nc')


# Part 2
for model in scenarios:
    for run in scenarios[model]:
        modeldir = '/work/scratch-nopw/pmcjs/utci_projections_1deg/%s/historical/%s/' % (model, run)
        outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections_1deg_exceedence/%s/historical/%s/' % (model, run)
        mkdir_p(outdir)
        cube_model = iris.load_cube(modeldir + 'utci_3hr_*.nc')
        #result26 = cube_model.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+26)
        #result32 = cube_model.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+32)
        #result38 = cube_model.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+38)
        #result46 = cube_model.collapsed('time', iris.analysis.PROPORTION, function=lambda values: values > 273.15+46)
#        iris.save(result, outdir + 'utci_3hr_%s_%s_%s_gn_%4d.nc' % (model, scenario, run, year))
#        sys.stdout.write('%s %s %s %s success\n' % (model, run, scenario, year))
