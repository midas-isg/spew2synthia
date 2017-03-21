path="/mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0"
fips = '01077010100'
puma = '100'
#fips = '42003457100'
#puma = '1807'
#fips = '42065950700'
#puma = '1300'

code = fips[:5]

path_usa = path + '/americas/northern_america/usa'
st = fips[:2]
path_state_output = path_usa + '/' + st + '/output'
path_env = path_state_output + '/environments'
path_puma_eco = path_state_output + '/output_' + puma + '/eco/'

# local files
#path_env = './spew_sample/env'
#path_puma_eco = './spew_sample'

file_pp = path_puma_eco + '/people_' + fips + '.csv'
file_hh = path_puma_eco + '/household_' + fips + '.csv'

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