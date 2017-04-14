#!/usr/bin/env bash

module load python/3.5.1

python3 state.py; python3 county.py; ./usa_from_states.sh

echo DONE!