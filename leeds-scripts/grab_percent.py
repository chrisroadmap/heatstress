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

era5heatdir = '/nfs/b0110/Data/ERA5-HEAT/regrid_1deg/'
outdir = '/nfs/b0110/Data/ERA5-HEAT/percentiles_1deg/'
mkdir_p(outdir)

for year in tqdm(range(1985, 2015)):
    cube_era5 = iris.load_cube(era5heatdir + 'ECMWF_utci_%4d_v1.0_con.nc' % year)
    #equalise_attributes(cube_era5)
    #unify_time_units(cube_era5)
    #cube_era5 = cube_era5.concatenate_cube()

    result = cube_era5.collapsed('time', iris.analysis.PERCENTILE, percent=[95, 98, 99, 99.5, 99.9, 100])
    iris.save(result, outdir + 'ECMWF_utci_%4d_v1.0_con.nc' % year)
