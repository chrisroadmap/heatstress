#!/usr/bin/env python
# coding: utf-8

# # Bias correction for the UTCI dataset
# 
# Note: the ERA5-HEAT data are not on JASMIN, so this is a "run at Leeds" notebook. The output distributions for each model will be added to this GitHub however.
# 
# Here we use the ERA5-HEAT dataset from 1985 to 2014 and compare this to the derived UTCI from each climate model.
# 
# Therefore, instead of bias-correcting temperature or any other variables, we bias correct the derived UTCI.
# 
# We therefore assume that ERA5-HEAT is "Truth"! To be fair, I would probably bias correct the individual variables against their ERA5 counterparts. For all except temperature this becomes a little tricky and subjective.
# 
# Update 13/05/2021: we have to regrid ERA5-HEAT to model data and not the other way around as the data and computation overhead is just too big to have everything on a 1/4 degree grid.

# In[ ]:


import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import iris.analysis.cartography
import iris.coord_categorisation
import matplotlib.pyplot as pl
from climateforcing.utils import mkdir_p
import numpy as np
import pickle
import scipy.stats as st
from tqdm import tqdm


# ## Obtain historical "training" distributions
# 
# If regridding to ERA5, we need to run yearly and save output because of memory errors. This might not be required for regridding from ERA5 to each model.

# In[ ]:


era5heatdir = '/nfs/b0110/Data/ERA5-HEAT/'
modeldir = '/nfs/b0110/Data/heatstress/HadGEM3-GC31-LL/historical/r1i1p1f3/'
regriddir = '/nfs/b0110/Data/ERA5-HEAT/regrid/HadGEM3-GC31-LL/'
mkdir_p(regriddir)

for year in tqdm(range(1985, 2015)):
    cube_era5 = iris.load(era5heatdir + 'ECMWF_utci_%4d????_v1.0_con.nc' % year)
    equalise_attributes(cube_era5)
    unify_time_units(cube_era5)
    for cu in cube_era5:
        cu.coord('time').points = cu.coord('time').points.astype(int)
    cube_era5 = cube_era5.concatenate_cube()
    cube_era5.coord('longitude').guess_bounds()
    cube_era5.coord('latitude').guess_bounds()

    cube_model = iris.load(modeldir + 'utci_3hr_HadGEM3-GC31-LL_historical_r1i1p1f3_gn_%d01010300-%d01010000.nc' % (year, year+1))
    cube_model = cube_model.concatenate_cube()
    # regrid the ERA5 to the model
    if year==1985:
        regridder = iris.analysis.AreaWeighted().regridder(cube_era5, cube_model)
    cube_era5_regrid = regridder(cube_era5)
    # save the output
    iris.save(cube_era5_regrid, regriddir + 'ECMWF_utci_%d_v1.0_con.nc' % year)


# In[ ]:


# load up the regridding annual chunks and concatenate
cube_era5_regrid = iris.load(regriddir + 'ECMWF_utci_*_v1.0_con.nc')
equalise_attributes(cube_era5_regrid)
unify_time_units(cube_era5_regrid)
for cu in cube_era5_regrid:
    cu.coord('time').points = cu.coord('time').points.astype(int)
cube_era5_regrid = cube_era5_regrid.concatenate_cube()


# In[ ]:


cube_era5_regrid.coord('latitude')[28]


# In[ ]:


cube_era5_regrid.coord('longitude')[191]


# In[ ]:


cube_model.coord('latitude')[115]


# In[ ]:


cube_model = iris.load(modeldir + 'utci_3hr_HadGEM3-GC31-LL_historical_r1i1p1f3_gn_*.nc')
cube_model = cube_model.concatenate_cube()


# In[ ]:


model_data = cube_model.data
era5_data = cube_era5_regrid.data


# In[ ]:


leeds_model = model_data[:,115,191]
leeds_era5 = era5_data[:,115,191]


# In[ ]:


pl.hist(leeds_model, density=True, label='HadGEM3-GC31-LL', alpha=0.3)
pl.hist(leeds_era5, density=True, label='ERA5-HEAT', alpha=0.3)
pl.legend()
pl.title('Leeds grid cell, 1985-2014')


# In[ ]:


# save the output
iris.save(cube_model_regrid, '/nfs/b0110/Data/ERA5-HEAT/regrid_hadgem3_1985-2014.nc')


# In[ ]:


model_params = {}
model_params['a'] = np.zeros((cube_model_regrid.shape[1:3]))
model_params['loc'] = np.zeros((cube_model_regrid.shape[1:3]))
model_params['scale'] = np.zeros((cube_model_regrid.shape[1:3]))
model_params['lat'] = cube_model_regrid.coord('latitude').points
model_params['lon'] = cube_model_regrid.coord('longitude').points

era5_params = {}
era5_params['a'] = np.zeros((cube_model_regrid.shape[1:3]))
era5_params['loc'] = np.zeros((cube_model_regrid.shape[1:3]))
era5_params['scale'] = np.zeros((cube_model_regrid.shape[1:3]))
era5_params['lat'] = cube_model_regrid.coord('latitude').points
era5_params['lon'] = cube_model_regrid.coord('longitude').points


# In[ ]:


st.skewnorm.fit(leeds_model)


# In[ ]:


for ilat in range(len(model_params['lat'])):
    for ilon in range(len(model_params['lon'])):
        model_params['a'][ilat, lon], model_params['loc'][ilat, lon], model_params['scale'][ilat, lon] = (
            st.skewnorm.fit(model_data[:, ilat, ilon])
        )
        era5_params['a'][ilat, lon], era5_params['loc'][ilat, lon], era5_params['scale'][ilat, lon] = (
            st.skewnorm.fit(era5_data[:, ilat, ilon])
        )


# In[ ]:


pl.hist(leeds_model, density=True, label='HadGEM3-GC31-LL', alpha=0.3, bins=50)
pl.hist(leeds_era5, density=True, label='ERA5-HEAT', alpha=0.3, bins=50)
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), model_params['a'][145,715], model_params['loc'][145,715], model_params['scale'][145,715]), color='tab:blue')
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), era5_params['a'][145,715], era5_params['loc'][145,715], era5_params['scale'][145,715]), color='tab:orange')
pl.legend()
pl.title('Leeds grid cell, 1985-2014')


# ## How to bias correct
# 
# $\hat{x}_{m,p}(t) = F^{-1}_{o,h} ( F_{m,h} (x_{m,p}(t)) )$
# 
# - $x_{m,p}$ is the future predicted variable, i.e. the SSP value from the climate model
# - $F_{m,h}$ is the CDF of the historical period in the climate model
# - $F_{o,h}$ is the CDF of the historical period in the observations (or in this case, ERA5)

# In[ ]:


# F_{m,h}
st.skewnorm.cdf(290, model_params['a'], model_params['loc'], model_params['scale'])


# In[ ]:


# F^{-1}_{o,h}
st.skewnorm.ppf(0.9474796515226899, era5_params['a'], era5_params['loc'], era5_params['scale'])


# In[ ]:


# transfer function
def bias_correct(x, model_params, obs_params):
    cdf = st.skewnorm.cdf(x, model_params['a'], model_params['loc'], model_params['scale'])
    x_hat = st.skewnorm.ppf(cdf, obs_params['a'], obs_params['loc'], obs_params['scale'])
    return x_hat


# ## Bias correct future simulations
# 
# For now, just use 2100

# In[ ]:


modelfuturedir = '/nfs/b0110/Data/heatstress/HadGEM3-GC31-LL/ssp585/r1i1p1f3/'
cube_model_future = iris.load(modelfuturedir + 'utci_3hr_HadGEM3-GC31-LL_ssp585_r1i1p1f3_gn_210001010300-210101010000.nc')
cube_model_future = cube_model_future.concatenate_cube()


# In[ ]:


cube_model_future


# In[ ]:


cube_model_future_regrid = regridder(cube_model_future)


# In[ ]:


leeds_model_future = cube_model_future_regrid[:,145,715].data


# In[ ]:


pl.hist(leeds_model, density=True, label='HadGEM3-GC31-LL 1985', alpha=0.3)
pl.hist(leeds_era5, density=True, label='ERA5-HEAT', alpha=0.3)
pl.hist(leeds_model_future, density=True, label='HadGEM3-GC31-LL 2100', alpha=0.3)
pl.legend()
pl.title('Leeds grid cell')


# In[ ]:


with open('/nfs/b0110/Data/ERA5-HEAT/regrid_hadgem3_2100.npy', 'wb') as f:
    pickle.dump(cube_model_future_regrid, f, protocol=pickle.HIGHEST_PROTOCOL)


# In[ ]:


model_future_params = {}


# In[ ]:


st.skewnorm.fit(leeds_model_future)


# In[ ]:


model_future_params['a'], model_future_params['loc'], model_future_params['scale'] = st.skewnorm.fit(leeds_model_future)


# In[ ]:


pl.hist(leeds_model, density=True, label='HadGEM3-GC31-LL 1985', alpha=0.3, bins=50)
pl.hist(leeds_era5, density=True, label='ERA5-HEAT', alpha=0.3, bins=50)
pl.hist(leeds_model_future, density=True, label='HadGEM3-GC31-LL 2100', alpha=0.3, bins=50)
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), model_params['a'], model_params['loc'], model_params['scale']), color='tab:blue')
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), era5_params['a'], era5_params['loc'], era5_params['scale']), color='tab:orange')
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), model_future_params['a'], model_future_params['loc'], model_future_params['scale']), color='tab:green')
pl.legend()
pl.title('Leeds grid cell')


# In[ ]:


# bias correct the Leeds 2100 projections
leeds_model_future_biascorrected = bias_correct(leeds_model_future, model_params, era5_params)


# In[ ]:


pl.hist(leeds_model, density=True, label='HadGEM3-GC31-LL 1985', alpha=0.3, bins=50)
pl.hist(leeds_era5, density=True, label='ERA5-HEAT', alpha=0.3, bins=50)
pl.hist(leeds_model_future, density=True, label='HadGEM3-GC31-LL 2100', alpha=0.3, bins=50)
pl.hist(leeds_model_future_biascorrected, density=True, label='Bias-corrected 2100', alpha=0.3, bins=50)

pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), model_params['a'], model_params['loc'], model_params['scale']), color='tab:blue')
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), era5_params['a'], era5_params['loc'], era5_params['scale']), color='tab:orange')
pl.plot(np.arange(240, 305), st.skewnorm.pdf(np.arange(240, 305), model_future_params['a'], model_future_params['loc'], model_future_params['scale']), color='tab:green')
pl.legend()
pl.title('Leeds grid cell')


# In[ ]:




