#!/bin/bash
#SBATCH -p short-serial
#SBATCH -o job_output/%j.out
#SBATCH -e job_output/%j.err
#SBATCH -t 03:00:00
#SBATCH --mem=32000  # 64M needed for HadGEM3-MM, else 32M usually sufficient

conda activate heatstress
./extract_stats.py
