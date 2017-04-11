# SPEW to Synthia

## What you'll need
- access to host spew.olympus.psc.edu or similar
- read access to path /mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0

## Stack
- **Python**[tested with 3.5.1]
- **Shapely**: to translate from [WKB](https://en.wikipedia.org/wiki/Well-known_text#Well-known_binary)to Latitude and Longitude. [tested with 1.5.17]

## Run on spew.olympus.psc.edu
To load python:

`module load python/3.5.1`

To go to the script directory:

`cd spew2synthia` 

### Only for the first time
To install Shapely as a user if it is not available globally:

`pip3 install --user shapely`

### For USA states
To translate all states in the USA:

`python3 state.py`

Note: 
- Output files will be generated in directory ../populations/2010_ver1_<state FIPS #>
- Log files will be generated in ./logs
  - Overall stdout will be logged into file states.< timestamp >.
  - All stdout of each state will be logged into file <state FIPS #>.out. *Note:* if the .out file exists, the script will skip the state.
  - If there is any error, it will be logged into file <state FIPS #>.err.

### For USA counties
To translate all counties in the USA:

`python3 county.py`

Note: 
- Output files will be generated in directory ../populations/2010_ver1_<county FIPS #>
- Log files will be generated in ./logs
  - Overall stdout will be logged into file counties.< timestamp >.
  - All stdout of each state will be logged into file <state FIPS #>/<county FIPS #>.out. *Note:* if the .out file exists, the script will skip the county.
  - If there is any error, it will be logged into file <state FIPS #>/<county FIPS #>.err.

### For other countries (excluding USA)
To translate all countries using IPUMS and Canada data sources:

`python3 country.py`

Note: 
- Output files will be generated in directory ../populations/spew_1.2.0_<country ISO 3166-1 alpha-3>
- Log files will be generated in ./logs
  - Overall stdout will be logged into file countries.< timestamp >.
  - All stdout of each state will be logged into file <country ISO 3166-1 alpha-3>.out. *Note:* if the .out file exists, the script will skip the county.
  - If there is any error, it will be logged into file <country ISO 3166-1 alpha-3>.err.
