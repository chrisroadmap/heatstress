#!/usr/bin/env python

"""
This script calculates the annual percentiles for ERA5-HEAT and HadGEM3 historical
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
from tqdm import tqdm

#era5heatdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg/'
#outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg_percentiles/'
#mkdir_p(outdir)
#
#for year in tqdm(range(1985, 2015)):
#    cube_era5 = iris.load_cube(era5heatdir + 'ECMWF_utci_%4d_v1.0_con.nc' % year)
#    result = cube_era5.collapsed('time', iris.analysis.PERCENTILE, percent=[95, 98, 99, 99.5, 99.9, 100])
#    iris.save(result, outdir + 'ECMWF_utci_%4d_v1.0_con.nc' % year)
#
modeldir = '/work/scratch-nopw/pmcjs/utci_projections_1deg/HadGEM3-GC31-LL/historical/r1i1p1f3/'
outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections_1deg_percentiles/HadGEM3-GC31-LL/historical/r1i1p1f3/'

mkdir_p(outdir)
for year in tqdm(range(1985, 2015)):
    cube_model = iris.load_cube(modeldir + 'utci_3hr_HadGEM3-GC31-LL_historical_r1i1p1f3_gn_%4d01010300-%4d01010000.nc' % (year, year+1))
    cube_model.coord('time').points = cube_model.coord('time').points - 1/16  # put on radiation timesteps
    result = cube_model.collapsed('time', iris.analysis.PERCENTILE, percent=[95, 98, 99, 99.5, 99.9, 100])
    iris.save(result, outdir + 'utci_3hr_HadGEM3-GC31-LL_historical_r1i1p1f3_gn_%4d.nc' % year)
