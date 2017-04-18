path="/mnt/lustre0/machines/data.olympus.psc.edu/srv/apache/data/syneco/spew_1.2.0"
path_usa = path + '/americas/northern_america/usa'
pattern_state_output = path_usa + '/{state}/output'
pattern_env = pattern_state_output + '/environments'
pattern_csv = pattern_state_output + '/**/{prefix}*.csv'

pattern_country = path + '/*/*/{iso3}'

pp_prefix = 'people_'
hh_prefix = 'household_'
