path="/mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0"
path_usa = path + '/americas/northern_america/usa'
pattern_state_output = path_usa + '/{state}/output'
pattern_env = pattern_state_output + '/environments'
pattern_csv = pattern_state_output + '/**/{prefix}*.csv'

pattern_country = path + '/*/*/{iso3}'

pp_prefix = 'people_'
hh_prefix = 'household_'
pp_map = {'SERIALNO':'serialno',    # us, ca & ipums
          'place_id': 'stcotrbg',   # us, ca & ipums
          'SYNTHETIC_HID': 'sp_hh_id',  # us, ca & ipums
          'SEX': 'sex',     # us, ca & ipums
          'AGEP': 'age',     # us
          # ca
          'AGE': 'age',   # ipums
          'RELP': 'relate',     # us
          # ca & ipums
          'RAC1P': 'race',    # us
          # ca
          'RACE': 'race',    # ipums
          'SYNTHETIC_PID': 'sp_id',     # us, ca & ipums
          'school_id': 'sp_school_id',    # us
          # ca
          'SCHOOL': 'sp_school_id',    # ipums
          'workplace_id': 'sp_work_id'    # us
          # ca, ipums
          }
hh_map = {'SERIALNO':'serialno',    # us, ca & ipums
          'place_id': 'stcotrbg',   # us, ca & ipums
          'SYNTHETIC_HID': 'sp_id', # us, ca & ipums
          'HINCP': 'hh_income',     # us
          'INCTAX': 'hh_income',     # ca
          'INCTOT': 'hh_income',     # ipums
          'NP': 'hh_size',          # us
          # ca
          'PERSONS': 'hh_size',     # ipums
          'AGEP': 'hh_age',     # us
          # ca
          'AGE': 'hh_age',   # ipums
          'RELP': 'relate',     # us
          # ca & ipums
          'RAC1P': 'hh_race',    # us
          # ca
          'RACE': 'hh_race'    # ipums
          }
