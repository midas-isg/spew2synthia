#!/usr/bin/env bash

module load python/3.5.1

echo "translating all states of the USA..."
python3 state.py

echo "translating all counties in all states of the USA..."
python3 county.py

echo "combinding all states of the USA into a country..."
./usa_from_states.sh >logs/usa.log 2>logs/usa.err

echo "DONE for USA!"