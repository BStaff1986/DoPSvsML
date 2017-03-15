'''
Injury Data from http://nhlinjuryviz.blogspot.ca/p/index-page.html
'''

import pandas as pd
import re

# TODO: Get victim's team

inj = pd.read_csv('NHL_Injuries.csv')

# TODO: Change this CSV to the new stats one
dops = pd.read_csv('Scrubbed_CSV.csv', encoding='latin1')

def reformat_season_year(row):
    '''
    Uses regex to parse the starting year of the season
    '''
    
    year = re.compile(r'''
                          ([2][0]\d{2})
                                                   
                          ''', re.VERBOSE)
    return int(re.search(year, row).group(1))

inj['start_year'] = inj['Season'].apply(reformat_season_year)

# Eliminate the injuries that are not caused by things players get 
# suspended for.
elim_injs = ['Pneumonia', 'Thyroid', 'Migraine', 'Blood clots',
             'Sinus', 'Stomach', 'Bronchitis', 'Vertigo', 'Heart',
             'Dizziness', 'Appendectomy', 'Fatigue', 'Illness', 'Flu']
inj = inj[-inj['Injury Type'].isin(elim_injs)]

victim_names = dops['victim'].unique()
#victim_names = victim_names[victim_names != 'No Player Victim']

vic_set = set(dops['vic_last_name'])
inj_set = set(inj['Player'])

intersect = inj_set.intersection(vic_set)
#intersect = set(['Zucker'])

# See how many injuries and suspension year match up
inj_connect = pd.DataFrame(columns=['victim', 'date', 'games_missed',
                                         'inj_type', 'susp_act'])

# TODO: Multiple injuries in a year should appear as separate lines
# TODO: Maybe get victim's team first
# USE df[(df['x'] == 'a') & (df['y'] == 'b')]!!!
for player in intersect:
    dops_df = dops[dops['vic_last_name'] == player]
    inj_df = inj[inj['Player'] == player]
     
    new_year_months = [1,2,3,4,5,6,7]
    for index, row in dops_df.iterrows():
        off_year = row['off_year']
        if row['off_month'] in new_year_months:
            off_year -= 1   
        
        if off_year in inj_df['start_year'].values:
            inj_year = inj_df[inj_df['start_year'] == off_year]
            #print(inj_year)
            victim = row['vic_last_name']
            date = row['off_date']
            print(date)
            g_miss = inj_year['Games Missed']
            print(g_miss)
            inj_type = inj_year['Injury Type']
            susp_act = row['offense_cat']
                
        inj_connect.loc[len(inj_susp_connect)] = [victim, date,
                             g_miss, inj_type, susp_act]
    break        
        
print(len(inj_susp_connect))
