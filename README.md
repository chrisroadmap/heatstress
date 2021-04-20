# heatstress
Analysis of heat stress from CMIP6 models

PLEASE NOTE THIS DOESN'T WORK YET ON JASMIN

## Getting started
It's best to do this in conda:

1. Download the miniconda3 installer
2. Install conda
3. Create a new environment:

```
$ conda create --name heatstress python=3.7
```

4. Activate the environment

```
$ conda activate heatstress
```

5. Get iris (we don't want version 3 right now, it doesn't work with cftime 1.4.1)

```
(heatstress) $ conda install -c conda-forge iris==2.4.0
```

6. install all of the other dependencies needed to run this package

```
(heatstress) $ cd ~/heatstress  # or whatever the path to your local repo is
(heatstress) $ pip install -r requirements.txt
```

7. To ensure that notebooks are cleaned to enable better version control, I use `nbstripout` (https://github.com/kynan/nbstripout). This automatically sets up a pre-commit hook to clean notebooks of outputs and cell execution counts. After all is installed, run

```
(heatstress) $ nbstripout --install
```
