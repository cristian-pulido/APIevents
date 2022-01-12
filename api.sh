#!/bin/bash
WORKING_DIR=/home/cpulido/TM/APIevents/api/
ACTIVATE_PATH=/home/cpulido/.virtualenvs/tmenv/bin/activate
cd ${WORKING_DIR}
. ${ACTIVATE_PATH}
exec $@


