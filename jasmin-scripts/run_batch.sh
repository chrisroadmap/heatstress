#!/bin/bash
mkdir -p job_output
#SBATCH -p short-serial
#SBATCH -o job_output/%j.out
#SBATCH -e job_output/%j.err
#SBATCH -t 24:00:00
#SBATCH --mem=32000

conda activate heatstress
./run_utci.py IITM-ESM ssp585 r1i1p1f1

## Usage:
## make sure you are in the correct directory: from the repo base:
## $ cd jasmin-scripts

## then
## $ sbatch run_batch.sh 

##### Below here are snippets that you can ignore
##### ${SLURM_ARRAY_TASK_ID}
##### sbatch --array=0-157   # make sbatch CAPS
##### this could be done if we could assign a model/scenario/run ID number to each combination with the SLURM_ARRAY_TASK_ID command
