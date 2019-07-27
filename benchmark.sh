#!/bin/bash

rm -rf output

source env/bin/activate #
reprobench server &  #

reprobench bootstrap && reprobench manage local run #

killall reprobench #

reprobench analyze #

