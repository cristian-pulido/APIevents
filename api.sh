#!/bin/bash
WORKING_DIR=/home/cpulido/TM/APIevents/api
ACTIVATE_PATH=activate tmenv
cd ${WORKING_DIR}
eval "$(conda activate tmenv)"
exec $@


