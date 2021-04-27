# heatstress
Analysis of heat stress from CMIP6 models. These instructions are incomplete!

## Getting started: JASMIN

1. Open a JASMIN notebook server in the Python+JasPy environment
2. run jasmin-setup.ipynb

This will set up the environment within the JASMIN notebook and creates a conda environment called `heatstress` that contains the necessary packages. You can use the `heatstress` environment when starting up new JupyterNotebooks for analysis work.

3. If you want to run any of the jasmin-scripts, from the JASMIN compute servers on the command line (e.g. sci1, sci2) do

```
$ module load jaspy
$ conda init
```

Close your shell, restart your shell, then

```
$ conda activate heatstress
```

This should work if you have done steps 1 and 2 above.

## Getting started: on Leeds server, or personal computer

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
