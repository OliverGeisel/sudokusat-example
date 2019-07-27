#!/bin/bash

# Usage: ./my_solver.sh [sat_solver] [path_to_task]
SATSOLVER=$1 #


me=$(dirname $(realpath "$0")) #
cd $me #
TASK=$2 #

python3 ../main.py $TASK $SATSOLVER #
echo "done!"

