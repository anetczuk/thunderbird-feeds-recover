#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


##
## check Python version
##
python3_version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python3_version" ]]; then
    echo "No Python! Python is required for the project." 
    exit 1
fi
#python3_number=$(echo "${python3_version//./}")
#if [[ "$python3_number" -lt "370" ]]; then 
#    echo "Invalid Python version! Required version at least 3.7.0" 
#    exit 1
#fi


## ensure required version of pip3
#pip3 install --upgrade 'pip>=18.0'


## install requirements
pip3 install -r $SCRIPT_DIR/requirements.txt


## sudo apt-get install python3-tk


echo -e "\ninstallation done\n"
