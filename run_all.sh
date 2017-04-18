#!/usr/bin/env bash

module load python/3.5.1

echo "translating all countries except USA..."
python3 country.py

echo "translating USA ..."
./usa_all.sh

echo "DONE for all countries!"