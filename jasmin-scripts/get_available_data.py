import glob
import pandas as pd

variables = ['tas', 'huss', 'uas', 'vas', 'rsds', 'rsdsdiff', 'rsus', 'rlds', 'rlus']

#for variable in variables:
dirlist = sorted(glob.glob('/badc/cmip6/data/CMIP6/ScenarioMIP/*/*/*/*/3hr/*/g*/latest/'))
insts = [i.split('/')[6] for i in dirlist]
models = [i.split('/')[7] for i in dirlist]
scens = [i.split('/')[8] for i in dirlist]
runs = [i.split('/')[9] for i in dirlist]
vars = [i.split('/')[11] for i in dirlist]

df = pd.DataFrame(list(zip(insts, models, scens, runs, vars)),
               columns = ['institution', 'model', 'scenario', 'run', 'variable'])


dirlist = sorted(glob.glob('/badc/cmip6/data/CMIP6/CMIP/*/*/historical/*/3hr/*/g*/latest/'))
insts = [i.split('/')[6] for i in dirlist]
models = [i.split('/')[7] for i in dirlist]
scens = [i.split('/')[8] for i in dirlist]  # always historical
runs = [i.split('/')[9] for i in dirlist]
vars = [i.split('/')[11] for i in dirlist]

df_hist = pd.DataFrame(list(zip(insts, models, scens, runs, vars)),
               columns = ['institution', 'model', 'scenario', 'run', 'variable'])


models_out = []
scens_out = []
runs_out = []

for model in df.model.unique():
    for scenario in df[df['model']==model].scenario.unique():
        for run in df[(df['model']==model) & (df['scenario']==scenario)].run.unique():
            vars_exist = df[(df['model']==model) & (df['scenario']==scenario) & (df['run']==run)].variable.tolist()
            count = 0
            for variable in variables:
                if variable in vars_exist and variable in df_hist[(df_hist['model']==model) & (df_hist['run']==run)].variable.tolist():
                    count=count+1
            if count==9:
                models_out.append(model)
                scens_out.append(scenario)
                runs_out.append(run)

df_out = pd.DataFrame(list(zip(models_out, scens_out, runs_out)), columns=['model', 'scenario', 'run'])

df_out.to_csv('../data/3hr_models.csv')
