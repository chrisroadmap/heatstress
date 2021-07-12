#!/bin/bash
#SBATCH -p short-serial
#SBATCH -o job_output/%j.out
#SBATCH -e job_output/%j.err
#SBATCH -t 01:00:00
#SBATCH --mem=64000

conda activate heatstress
./bias_correct_exceedence_pt1.py
