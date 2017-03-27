path="/mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0"
path_usa = path + '/americas/northern_america/usa'
pattern_state_output = path_usa + '/{state}/output'
pattern_env = pattern_state_output + '/environments'
pattern_csv = pattern_state_output + '/**/{prefix}*.csv'
pp_prefix = 'people_'
hh_prefix = 'household_'

pp_map = {'SERIALNO':'serialno',
          'place_id': 'stcotrbg',
          'SYNTHETIC_HID': 'sp_hh_id',
          'SEX': 'sex',
          'AGEP': 'age',
          'RELP': 'relate',
          'RAC1P': 'race',
          'SYNTHETIC_PID': 'sp_id',
          'school_id': 'sp_school_id',
          'workplace_id': 'sp_work_id'}
hh_map = {'SERIALNO':'serialno',
          'place_id': 'stcotrbg',
          'SYNTHETIC_HID': 'sp_id',
          'HINCP': 'hh_income',
          'NP': 'hh_size',
          'AGEP': 'hh_age',
          'RELP': 'relate',
          'RAC1P': 'hh_race'}
wp_map = {'"workplace_id"': 'sp_id','"employees"': 'workers'}
sc_map = {'"School"': 'name',
          '"ID"': 'sp_id',
          '"CoNo"':'county', # TODO # not name
          '"StNo"': 'stabbr', # TODO # not abbr
          '"Long"': 'longitude',
          '"Lat"':'latitude',
          '"Students"': 'total'}