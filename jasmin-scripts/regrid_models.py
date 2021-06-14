#!/usr/bin/env python

"""
This script regrids the climate model output data to 1x1 degree.
"""

import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import iris.analysis.cartography
import iris.coord_categorisation
import numpy as np
import glob
from climateforcing.utils import mkdir_p
import sys

# Make a dummy grid
latitude = iris.coords.DimCoord(
    np.arange(-89.5,90,1),
    standard_name='latitude',
    units='degrees',
    long_name='Latitude',
    var_name='lat',
    coord_system=None
)
longitude = iris.coords.DimCoord(
    np.arange(-179.5,180,1),
    standard_name='longitude',
    long_name='Longitude',
    var_name='lon',
    units='degrees',
    circular=True,
    coord_system=None
)

ny = len(latitude.points)
nx = len(longitude.points)

dummy_data = np.zeros((ny, nx))
dummy_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
dummy_cube.coord('longitude').guess_bounds()
dummy_cube.coord('latitude').guess_bounds()

# do the regrid and save output
#origdir = '/gws/pw/j05/cop26_hackathons/bristol/project10/utci_projections/'
origdir = '/work/scratch-nopw/pmcjs/'
regriddir = '/work/scratch-nopw/pmcjs/utci_projections_1deg/'

#models = ['HadGEM3-GC31-LL', 'BCC-CSM2-MR', 'CMCC-ESM2']
#runs = {
#    'HadGEM3-GC31-LL': ['r1i1p1f3'],
#    'BCC-CSM2-MR': ['r1i1p1f1'],
#    'CMCC-ESM2': ['r1i1p1f1'],
#}
#scenarios = {}
#scenarios['HadGEM3-GC31-LL'] = {}
#scenarios['BCC-CSM2-MR'] = {}
#scenarios['CMCC-ESM2'] = {}
#scenarios['HadGEM3-GC31-LL']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['BCC-CSM2-MR']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
#scenarios['CMCC-ESM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']

#models = ['CMCC-ESM2']
#runs = {
#    'CMCC-ESM2': ['r1i1p1f1']
#}
scenarios = {}
scenarios['ACCESS-CM2'] = {}
scenarios['ACCESS-CM2']['r1i1p1f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['CanESM5'] = {}
scenarios['CanESM5']['r1i1p2f1'] = ['historical', 'ssp126', 'ssp245', 'ssp585']
scenarios['CMCC-CM2-SR5'] = {}
scenarios['CMCC-CM2-SR5']['r1i1p1f1'] = ['historical', 'ssp245', 'ssp585']
scenarios['MRI-ESM2-0'] = {}
scenarios['MRI-ESM2-0']['r1i1p1f1'] = ['historical', 'ssp585']
scenarios['KACE-1-0-G'] = {}
scenarios['KACE-1-0-G']['r1i1p1f1'] = ['ssp245']
scenarios['HadGEM3-GC31-MM'] = {}
scenarios['HadGEM3-GC31-MM']['r1i1p1f3'] = ['historical', 'ssp126', 'ssp585']

for model in scenarios:
    for run in scenarios[model]:
        first_file=True
        for scenario in scenarios[model][run]:
            filelist = glob.glob(origdir + '%s/%s/%s/*.nc' % (model, scenario, run))
            for file in filelist:
                cube_orig = iris.load_cube(file)
                filename = file.split('/')[-1]
                if not cube_orig.coord('longitude').has_bounds():
                    cube_orig.coord('longitude').guess_bounds()
                if not cube_orig.coord('latitude').has_bounds():
                    cube_orig.coord('latitude').guess_bounds()

                # regrid the model to the new grid
                if first_file:
                    regridder = iris.analysis.AreaWeighted().regridder(cube_orig, dummy_cube)
                    first_file = False
                cube_regrid = regridder(cube_orig)
                # save the output
                outdir = regriddir + '%s/%s/%s/' % (model, scenario, run)
                mkdir_p(outdir)
                iris.save(cube_regrid, outdir + filename)
                sys.stdout.write(filename + ' success\n') 
