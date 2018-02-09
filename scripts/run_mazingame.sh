#!/bin/bash

#script to run mazingame within Docker container

#echo "argc = ${#*}"
#echo "argv = ${*}"

python mazingame-runner.py ${*}
