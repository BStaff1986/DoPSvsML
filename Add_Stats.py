from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import pickle
import json
import time
import re

dops = pd.read_csv('Scrubbed_CSV.csv', encoding='latin1')

def parse_id(string):
    '''
    With search suggestion data returned by NHL.com we can parse
    the player's NHL ID number
    '''
    if len(string) < 10:
        return None, None, None
    else:
        parse = re.compile(r'''
                   (?:p\|)
                   (\d*)
                   (?:\|)
                   (\w+)
                   (?:\|)
                   (\w+)
                   .*
                   ''',re.VERBOSE)
        parsed = parse.search(string)
        try:
            id_num = parsed.group(1)
            l_name = parsed.group(2)
            f_name = parsed.group(3)
        except AttributeError:
            return "Error", "Error", "Error"
        return id_num, f_name, l_name

def nhl_scrape():
    dops['vic_nhl_id'] = ''
    dops['off_nhl_id'] = ''
    
    for index, row in dops.iterrows():
        time.sleep(1)
        if type(row['vic_last_name']) is float:
            continue
        else:
            start_trio = row['vic_last_name'][0:3].lower()
            r = requests.get('https://suggest.svc.nhl.com/svc/suggest/v1/min_all/'
                     + start_trio + '/99999')
            result = json.loads(r.text)
            for ply in result['suggestions']:
                id_num, f_name, l_name = parse_id(ply)
                if (f_name == row['vic_first_name'] and
                    l_name == row['vic_last_name']):
                    dops.set_value(index, 'vic_nhl_id', id_num)
                    break
                            
                else:
                    print('NO MATCH')
                    
        if type(row['off_last_name']) is float:
            continue
        else:
            start_trio = row['off_last_name'][0:3].lower()
            r = requests.get('https://suggest.svc.nhl.com/svc/suggest/v1/min_all/'
                     + start_trio + '/99999')
            result = json.loads(r.text)
            for ply in result['suggestions']:
                id_num, f_name, l_name = parse_id(ply)
                if (f_name == row['off_first_name'] and
                    l_name == row['off_last_name']):
                    print(index, id_num, f_name, l_name)
                    dops.set_value(index, 'off_nhl_id', id_num)
                    break
                            
                else:
                    continue

'''
The below is for hockey-reference.com
The following will capture 
'''
def get_href_id(row, offender=True):
    '''
    Input DataFrame row
    Return identifiers for Hockey-Reference Scraping
    '''
    if offender == True:
        last_name = 'off_last_name'
        first_name = 'off_first_name'
    elif offender == False:
        last_name = 'vic_last_name'
        first_name = 'vic_first_name'
    
    new_year_months = [1,2,3,4,5,6]
        
    year = row['off_year']

    if row['off_month'] not in new_year_months:
        year += 1
    
    if type(row[last_name]) is float:
        return None, None, None
    else:
        id_ref = (row[last_name][0:5].lower() +\
                  row[first_name][0:2].lower()+\
                     '01')
        init_let = id_ref[0]
            
    return init_let, id_ref, year
            
   
def hockey_ref_scrape(values):
    '''
    Input hockey reference player ID information
    Returns gamelog table for year of incident
    '''
    init_let = values[0]
    id_ref = values[1]
    year = values[2]
    
    if init_let == None or id_ref == None or year == None:
        return None, None, None
    
    url = 'http://www.hockey-reference.com/players/'+\
            init_let + '/'+ id_ref + '/gamelog/'+ str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    table = soup.find_all('table',{'class':'row_summable'}) 
    
    return table[0]    

def parse_table(table, off_date):
    '''
    '''
    global new_cols
    
    rows = table.find_all('tr', {"id":re.compile(r'.*')})
    stat_dict = create_headers(rows[2])
    if new_cols == False:
        create_new_df_columns(rows[2])
        
    for row in rows:
        
        # Check if the game is before(or on) or after the offending date
        game_date = row.find_next('td', {'data-stat':'date_game'}).text
        good_date = date_checker(game_date, off_date)
                                
        if good_date:
            print(stat_dict)
            stat_dict = get_stats(stat_dict, row)
            print(stat_dict)
            print (''.center(20, '.'))
        else:
            return stat_dict
        
    return stat_dict
        
def create_headers(row):
    '''
    Input row of data.
    Parses the names of the categories we'd like to keep
    Returns a prepared dictionary
    '''
    stat_dict = {}
    skip = skip_headers()
    
    for datum in row:        
        if datum['data-stat'] in skip:
            continue
        else:
            stat_dict.setdefault(datum['data-stat'],0)
            
    return stat_dict

def skip_headers():
    '''
    Returns a list of the headers to be skipped when creating and updating
    the stats dictionary
    '''
    skip = ['ranker','date_game', 'team_id', 'game_location',
                'opp_id', 'game_result', 'shot_pct', 
                'faceoff_percentage_all']
    return skip
            
def date_checker(game_date, off_date):
    '''
    Input date of the game, and the date of suspension offense
    Returns True is the game is the same day or before offense
    Returns False if the game is after the suspension event
    '''
    off_date = datetime.strptime(off_date, '%Y-%m-%d')
    game_date = datetime.strptime(game_date, '%Y-%m-%d')
    
    if game_date <= off_date:
        return True
    else:
        return False
    
def get_stats(stat_dict, row):
    '''
    Input a row and the stat dictionary
    Parses the new values and adds them to the dictionary values
    Returns the dictionary
    '''
    skip = skip_headers()
    special = ['age', 'time_on_ice']
    
    for td in row.find_all('td'):
        stat = td['data-stat']
        if stat not in skip and stat not in special:
            stat_dict[stat] += int(td.text)
        elif stat == 'time_on_ice':
            toi = re.search(r'(\d{1,2}):?(\d{1,2})',td.text)
            toi_min = int(toi.group(1))
            toi_sec = int(toi.group(2))
            stat_dict[stat] = ((toi_min * 60) + toi_sec)
        elif stat == 'age':
            stat_dict[stat] = td.text
                     
    return stat_dict   

# Step 1: Get player ID
# Step 2: Scrape player's gamelog table
# Step 3: Collect season stats prior to offense date
#   Step 3b: Deal with Preseason offenses (like Shaw's, dops.loc[1])
# Step 4: Extract stat dictionaries into pandas DataFrame

def create_new_df_columns(row):
    '''
    Inserts new columns into dops dataframe
    '''
    
    global new_cols
    
    col_prefix = ['off_', 'vic_']
    
    skip = skip_headers()
    for prefix in col_prefix:
        for datum in row:
            if datum['data-stat'] in skip:
                continue
            else:
                string = prefix + datum['data-stat']
                dops[string] = 0
    
    
    new_cols = True
    
def stats_to_dataframe(off_stat, vic_stat, index):
    '''
    Input stats
    Add stats into dataframe
    '''
    off_keys = list(map(lambda stat: 'off_' + stat, off_stat.keys()))
    off_vals = [v for v in off_stats.values()]
    for x in zip(off_keys, off_vals):
        
    
        
    
new_cols = False
for index, row in dops.loc[0:1].iterrows():
    print(index)
    print(row['off_date'])
    print(row['off_last_name'])    
    
    off_table = hockey_ref_scrape(get_href_id(row, offender=True))
    
    if table:
        off_stats = parse_table(off_table, row['off_date'])
    else: 
        off_stats = None
    
    #table = hockey_ref_scrape(get_href_id(row, offender=True))

    

