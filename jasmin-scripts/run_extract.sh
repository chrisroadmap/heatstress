#!/bin/bash
#SBATCH -p short-serial
#SBATCH -o job_output/%j.out
#SBATCH -e job_output/%j.err
#SBATCH -t 16:00:00
#SBATCH --mem=16000  # one degree yearly, this will be more than sufficient?

conda activate heatstress
./extract_stats.py
