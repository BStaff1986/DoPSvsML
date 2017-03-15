import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/'

# Collect all the URL endings for the pages we want
pages = ['{}–{}_NHL_suspensions_and_fines'.format(str(n-1), 
         str(n)[-2:]) for n in range(2017, 2009, -1)]

# Create our DataFrame and preload the columns we will use
dops_df = pd.DataFrame(columns=('off_date', 'offender', 'off_team', 'offense', 
                                'dops_date', 'susp', 'forfeit_sal', 'fine'))



def suspension_table(table):
    '''
    This function goes through the Wikitables that hold data about player
    suspensions. 
    '''
    rows = table.find_all('tr')
    for row in rows[1:-1]:
        td = row.find_all('td')
        
        # NOTE: Some tables had data in a span class, others just text
        # which is why there are some try and except clauses.
        
        # td[0] holds Offense Date
        try:
            off_date = td[0].find('span',
                     {'style':'white-space:nowrap'}).text
        except AttributeError:
            off_date = td[0].text
        #td[1] holds the Offender's Name
        try:
            offender = td[1].find('span').text
        except:
            offender = td[1].text
        # td[2] holds Offender's Team                 
        off_team = td[2].text
        # td[3] holds a description of the Offense.             
        offense = td[3].text
        # td[4] holds the day the suspension was given out
        try:
            dops_date = td[4].find('span',
                     {'style':'white-space:nowrap'}).text
        except AttributeError:
            dops_date = td[4].text
        # td[5] holds the length of the suspension
        susp = td[5].text
        # td[6] holds the amount of salary forfeited from the suspension                 
        try:
            forfeit_sal = td[6].text
        except IndexError:
            forfeit_sal = 'N/A'
        # No fines so value is 0
        fine = 0

        # Store all the scraped values in the DataFrame                       
        dops_df.loc[len(dops_df)] = [off_date, offender, off_team, 
                               offense, dops_date, susp, forfeit_sal, fine]

        

def fines_table(table):
    '''
    This function goes through the tables that contain the fine data
    found in Wikipedia tables. 
    '''
    rows = table.find_all('tr')
    
    # NOTE: Some tables used span classes while others used simple text
    # which is why there are lots of try and except clauses
    
    for row in rows[1:-1]:
        td = row.find_all('td')
        # Get the date of offense
        try:
            off_date = td[0].find('span',
                     {'style':'white-space:nowrap'}).text
        except AttributeError:
            off_date = td[0].text
        # Get the offender's name            
        try:
            offender = td[1].find('span').text
        except AttributeError:
            offender = td[1].text
        # Get offending team
        off_team = td[2].text
        # Get the offense
        offense = td[3].text
        # Get the day the DoPS made a decision
        try:
            dops_date = td[4].find('span',{'style':'white-space:nowrap'}).text
        except AttributeError:
            dops_date = td[4].text
        susp = 0
        forfeit_sal = 0
        # Get the fine amount
        fine = td[5].text
                       
        dops_df.loc[len(dops_df)] = [off_date, offender, off_team, 
                               offense, dops_date, susp, forfeit_sal, fine]
        
def susp_table_oldstyle(table):
    '''
    Older Wikipedia tables did not have a column for the day the suspensions
    were applied and this shifted the data around so a new function was made.
    '''
    
    rows = table.find_all('tr')
    for row in rows[1:]:
        td = row.find_all('td')
        # Get the date of offense
        try:
            off_date = td[0].find('span',
                     {'style':'white-space:nowrap'}).text
        except AttributeError:
            off_date = td[0].text
        # Get the offender's name            
        try:
            offender = td[1].find('span').text
        except AttributeError:
            offender = td[1].text
        # Get offending team
        off_team = td[2].text
        # Get the offense
        offense = td[3].text
        # Get the day the DoPS made a decision
        dops_date = np.nan
        susp = td[4].text
        forfeit_sal = np.nan
        # Get the fine amount
        fine = np.nan
                       
        dops_df.loc[len(dops_df)] = [off_date, offender, off_team, 
                               offense, dops_date, susp, forfeit_sal, fine]
        
        
def fines_table_oldstyle(table):
    '''
    Older Wikipedia tables did not contain the date which the fines were 
    applied and this shifted the data around. As such, a new function was
    created
    '''
    
    rows = table.find_all('tr')
    for row in rows[1:]:
        td = row.find_all('td')
        # Get the date of offense
        try:
            off_date = td[0].find('span',
                     {'style':'white-space:nowrap'}).text
        except AttributeError:
            off_date = td[0].text
        # Get the offender's name            
        try:
            offender = td[1].find('span').text
        except AttributeError:
            offender = td[1].text
        # Get offending team
        off_team = td[2].text
        # Get the offense
        offense = td[3].text
        # Get the day the DoPS made a decision
        dops_date = np.nan
        susp = 0
        forfeit_sal = np.nan
        # Get the fine amount
        fine = td[4].text
                       
        dops_df.loc[len(dops_df)] = [off_date, offender, off_team, 
                               offense, dops_date, susp, forfeit_sal, fine]
        

def detect_page_table_type(page):
    '''
    Reads which year the Wiki pages covers and returns the appropriate 
    number of table headers to read in. 
    '''
    header_count ={
            '2016':[10,8],
            '2015':[10,8],
            '2014':[10,8],
            '2013':[11,9],
            '2012':[6,6],
            '2011':[6,6],
            '2010':[5,5],
            '2009':[5,5],
            }
    
    year = page[0:4]
  
    return header_count[year][0], header_count[year][1]

# Scrape each Wiki page for it's tables
for page in pages:
    print(page)    
    r = requests.get(url + page)
    bs = BeautifulSoup(r.text, features='lxml-xml')
    tables = bs.find_all('table',{'class':'wikitable sortable'})
    
    # Find the style of table by year
    susp_len, fine_len = detect_page_table_type(page)
    
    # Extract the data according to table type
    if susp_len > 6:
        for table in tables:
            headers = table.find_all('th')
            if len(headers) == susp_len:
                suspension_table(table)
            elif len(headers) == fine_len:
                fines_table(table)
            else:
                continue
    elif susp_len == 6:
        for table in tables:
            # Fine and suspensions are of equal length
            # Searching for length will determine type
            if '<th>Length</th>' in str(table.find_all('th')):
                suspension_table(table)
            else:
                fines_table(table)
    else:
        susp_table_oldstyle(tables[0])
        fines_table_oldstyle(tables[1])
    print(len(dops_df))
        
dops_df.to_csv('NHL_Suspensions.csv')