#!/usr/bin/env python

"""
This script calculates the annual percentiles for all models and scenarios
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
#scenarios['ACCESS-CM2'] = {}
#scenarios['ACCESS-CM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['CanESM5'] = {}
#scenarios['CanESM5']['r1i1p2f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['CMCC-CM2-SR5'] = {}
#scenarios['CMCC-CM2-SR5']['r1i1p1f1'] = ['historical', 'ssp245', 'ssp585']
#scenarios['MRI-ESM2-0'] = {}
#scenarios['MRI-ESM2-0']['r1i1p1f1'] = ['historical', 'ssp585']
scenarios['KACE-1-0-G'] = {}
scenarios['KACE-1-0-G']['r1i1p1f1'] = ['historical', 'ssp245']
#scenarios['HadGEM3-GC31-MM'] = {}
#scenarios['HadGEM3-GC31-MM']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp585']
#scenarios['HadGEM3-GC31-LL'] = {}
#scenarios['HadGEM3-GC31-LL']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['BCC-CSM2-MR'] = {}
#scenarios['BCC-CSM2-MR']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['CMCC-ESM2'] = {}
#scenarios['CMCC-ESM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']

for model in scenarios:
    # guess
    if model in ['KACE-1-0-G']:
        grid='gr'
    else:
        grid='gn'
    for run in scenarios[model]:
        for scenario in scenarios[model][run]:
            modeldir = '/work/scratch-nopw/pmcjs/utci_projections_1deg/%s/%s/%s/' % (model, scenario, run)
            outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections_1deg_percentiles/%s/%s/%s/' % (model, scenario, run)
            mkdir_p(outdir)
            if scenario == 'historical':
                firstyear = 1985
                lastyear = 2015
            else:
                firstyear = 2015
                lastyear = 2101
            for year in range(firstyear, lastyear):
                cube_model = iris.load_cube(modeldir + 'utci_3hr_%s_%s_%s_%s_%4d01010300-%4d01010000.nc' % (model, scenario, run, grid, year, (year+1)))
                if model in ['BCC-CSM2-MR', 'MRI-ESM2-0']:
                    cube_model.coord('time').points = cube_model.coord('time').points + 1/16
                elif model not in ['KACE-1-0-G']:
                    cube_model.coord('time').points = cube_model.coord('time').points - 1/16
                # put on radiation timesteps
                # KACE already well-behaved I think
                result = cube_model.collapsed('time', iris.analysis.PERCENTILE, percent=[95, 98, 99, 99.5, 99.9, 100])
                iris.save(result, outdir + 'utci_3hr_%s_%s_%s_gn_%4d.nc' % (model, scenario, run, year))
                sys.stdout.write('%s %s %s %s success\n' % (model, run, scenario, year))
