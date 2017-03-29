path="/mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0"
path_usa = path + '/americas/northern_america/usa'
pattern_state_output = path_usa + '/{state}/output'
pattern_env = pattern_state_output + '/environments'
pattern_csv = pattern_state_output + '/**/{prefix}*.csv'

pattern_country = path + '/*/*/{iso3}'

pp_prefix = 'people_'
hh_prefix = 'household_'
pp_map = {'SERIALNO':'serialno',    # us & ipums
          'place_id': 'stcotrbg',   # us & ipums
          'SYNTHETIC_HID': 'sp_hh_id',  # us & ipums
          'SEX': 'sex',     # us & ipums
          'AGEP': 'age',     # us
          'AGE': 'age',   # ipums
          'RELP': 'relate',     # us
          'PERNUM': 'relate',   # ipums
          'RAC1P': 'race',    # us
          'RACE': 'race',    # ipums
          'SYNTHETIC_PID': 'sp_id',     # us & ipums
          'school_id': 'sp_school_id',    # us
          'SCHOOL': 'sp_school_id',    # ipums
          'workplace_id': 'sp_work_id'    # us
          }
hh_map = {'SERIALNO':'serialno',    # us & ipums
          'place_id': 'stcotrbg',   # us & ipums
          'SYNTHETIC_HID': 'sp_id', # us & ipums
          'HINCP': 'hh_income',     # us
          'INCTOT': 'hh_income',     # ipums
          'NP': 'hh_size',          # us
          'PERSONS': 'hh_size',     # ipums
          'AGEP': 'hh_age',     # us
          'AGE': 'hh_age',   # ipums
          'RELP': 'relate',     # us
          'PERNUM': 'relate',   # ipums
          'RAC1P': 'hh_race',    # us
          'RACE': 'hh_race'    # ipums
          }
wp_map = {'"workplace_id"': 'sp_id','"employees"': 'workers'}
sc_map = {'"School"': 'name',
          '"ID"': 'sp_id',
          '"CoNo"':'county', # TODO # not name
          '"StNo"': 'stabbr', # TODO # not abbr
          '"Long"': 'longitude',
          '"Lat"':'latitude',
          '"Students"': 'total'}