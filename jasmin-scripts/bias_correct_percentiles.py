#!/usr/bin/env python

import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units

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

era5heatdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/era5-heat_1deg_percentiles/'
cube_era5 = iris.load(era5heatdir + 'ECMWF_utci_*_v1.0_con.nc')
equalise_attributes(cube_era5)
unify_time_units(cube_era5)
cube_era5 = cube_era5.merge().concatenate_cube()
cube_era5_mean = cube_era5.collapsed(['time'], iris.analysis.MEAN)

cube_model = {}
for model in scenarios:
    cube_model[model] = {}
    for run in scenarios[model]:
#        for scen in scenarios[model][run]:
        indir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections_1deg_percentiles/%s/historical/%s/' % (model, run)
        cube_model_temp = iris.load(indir + 'utci_3hr_*.nc')
        equalise_attributes(cube_model_temp)
        unify_time_units(cube_model_temp)
        cube_model[model][run] = cube_model_temp.merge().concatenate_cube()


cube_model_historical_mean = {}
for model in scenarios:
    cube_model_historical_mean[model] = {}
    for run in scenarios[model]:
        cube_model_historical_mean[model][run] = cube_model[model][run].collapsed(['time'], iris.analysis.MEAN)

cube_era5_mean.units = 'K'
outdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections_1deg_percentiles_bias/'
for model in scenarios:
    for run in scenarios[model]:
        cube_bias_offset = cube_model_historical_mean[model][run]-cube_era5_mean
        cube_bias_offset.var_name = 'utci'
        cube_bias_offset.long_name = 'Universal Thermal Climate Index'
        iris.save(cube_bias_offset, outdir + 'bias_%s_%s.nc' % (model, run))
