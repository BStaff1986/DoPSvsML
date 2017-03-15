import pandas as pd
from math import isnan
import re

dops = pd.read_csv('NHL_Suspensions.csv', encoding='latin1')

'''
Warning: Regex for victim's name currently will not work with names like
D'Amigo except for when parsing that last name in the form where the first
name comes first. Will not do so the other way around and not for offenders.
'''

# Column 1 = Date of Offense
# Column 2 = Offender Name
# Column 3 = Offender's Team
# Column 4 = Offense
# Column 5 = Day of DoPs decision
# Column 6 = Suspension Amount
# Column 7 = Forfeited Salary
# Column 8 = Fine

# TODO: Get Contract Info at https://www.capfriendly.com/


def re_parse_offense(row):
    '''
    This function goes through all the offense descriptions and, based on
    keywords it's able to parse using Regex, assigns a short description
    to be coded in later exploration
    '''
    re_exps = {r'.*abuse.*official' : 'Abuse of Official',
               r'Attempt.*' : 'Attempt to Injure',
               r'Automatic.*' : 'Automatic Suspension',
               r'Blindsid.*' : 'Blindsiding',
               r'Board.*' : 'Boarding',
               r'[Bb]utt-?end.*' : 'Butt-Ending',
               r'[Cc]harg.*' : 'Charging',
               r'Clip.*' : 'Clipping',
               r'([Cc]omment.*|[Cc]omplaint.*|[Gg]esture.*|[Ss]lur)' : 'Comments/Gestures',
               r'Cross.check.*' : 'Cross-checking',
               r'Diving.*' : 'Diving',
               r'Elbow.*': 'Elbowing',
               r'[Hh]ead-?butt.*' : 'Head-Butting',
               r'High.stick.*' : 'High-Stick',
               r'(Hit.*|Check.*) from behind':'Hitting from Behind',
               r'Illegal( check| hit)' : 'Illegal Check',
               r'(Inappropriate.*|conduct)' : 'Inappropriate Conduct',
               r'([Ii]nstigat.*|[Aa]ggress.*)' : 'Instigator',  
               r'Interfer.*' : 'Interference',
               r'Knee-on-knee.*' : 'Knee-on-knee',
               r'([Kk]ick.*|Kneeing)' : 'Kicking or Kneeing',
               r'([Ll]ate|[Ll]ow)?.*([Hh]it.|[Cc]heck)(to the head)?' : 'Illegal hit',# Late, low, to head
               r'[Ll]eaving.*bench' : 'Leaving Bench',
               r'[Pp]unch.*' : 'Punching',                            
               r'Roughing.*' : 'Roughing',
               r'Slash.*' : 'Slashing', 
               r'[Ss]lew.*' : 'Slew-footing',
               r'Spear.*': 'Spearing',
               r'[Tt]rip.*' : 'Tripping',
               r'.*[Vv]iolating' : 'Drugs',
               }
    for k,v in re_exps.items():
        if re.search(k, row):
            return v
        else:
            continue
    return 'NO PARSE' # Labels uncoded entries
        

def re_parse_victim(row):
    '''
    This function parses player names out of the description of the offenses
    '''
    
    errors = ['Substances Program','Health Program',
              'Star Game','Montreal Canadiens',
              'Vancouver Canucks','Maple Leafs','Red Wings',]
    
    vic = re.compile(r'''
                     (?:[A-Z]\w+ing)?
                     .*
                     (([A-Z]\w+\s[A-Z]\w+| # Regular names
                     [A-Z][.]\s?[A-Z][.]\s?\s[A-Z]\w+| # P. K.s and T.J.s
                     [A-Z]\w+\s[A-Z]'[A-Z]\w+ # D'Amigos
                     ))
                     ''', re.VERBOSE)
    try:
        if vic.search(row).group(1) in errors:
            return "No Player Victim"
        else:
            return vic.search(row).group(1)
    except AttributeError: 
        return "No Player Victim"
    
       
def re_parse_total_games(row):
    '''
    This finds the total number of games a player was suspended for.
    The regex assumes that the first number is the number of games suspended
    which is true for 99% of entries*
    
    (*Tortorella was suspended 15 days, which amounted to 6 games)
    '''
    
    games = re.compile(r'''
                       (\d+)
                       (?:\s.*)?
                       ''', re.VERBOSE)
    return int(re.search(games, row).group(1))

def re_parse_playoff_games(row):
    '''
    Uses regex to find the number of playoff games in the suspension
    '''
    
    post_games = re.compile(r'''
                          .*?
                          (\d+)
                          (?:\s[A-Z]{,3})?
                          (?:\s\d{4})?
                          \s
                          post-season.*                          
                          ''', re.VERBOSE)
    try:
        return int(re.search(post_games, row).group(1))
    except AttributeError:
        return 0
    
def re_parse_preseason_games(row):
    '''
    Uses regex to get the number of preseason games in the suspension
    '''
    
    pre_games = re.compile(r'''
                          .*?
                          (\d+)
                          (?:\s[A-Z]{,3})?
                          (?:\s\d{4})?
                          \s
                          pre-season.*                          
                          ''', re.VERBOSE)
    try:
        return int(re.search(pre_games, row).group(1))
    except AttributeError:
        return 0

def money_to_float(row):
    replacements = {"$":'', ",":""}
    if type(row) is str:
        try:
            return float(''.join([replacements.get(c,c) for c in row]))
        except ValueError:
            try:
                re_expr = re.compile(r'''
                          [$]
                          (\d+,\d+.\d+)
                          .*?                          
                          ''', re.VERBOSE)
                money = re.search(re_expr, row).group(1)
                return float(''.join([replacements.get(c,c) for c in money]))
            except AttributeError:
                return "ERROR"
    else:
        return 0
    
def get_year(row):
    '''
    This function pulls the year out of datetime object and returns
    just the year
    '''
    try:
        return int(row.year)
    except ValueError:
        return 0

def get_month(row):
    '''
    This function pulls the year out of datetime object and returns
    just the month
    '''
    try:
        return int(row.month)
    except ValueError:
        return 0

def get_day(row):
    '''
    This function pulls the year out of datetime object and returns
    just the day
    '''
    try:
        return int(row.day)
    except ValueError:
        return 0
    
def get_off_lastname(name):
    '''Parse the victim's last name'''
    non_player = ['No Player Victim', 'Team', 'Organization']
    if name in non_player:
        return None
    
    if ',' in name:
        reg_exp =  re.compile(r'(\w+)[,]?\s\w+')
        return reg_exp.findall(name).pop()
    
    else:
        reg_exp =  re.compile(r'.*\s(\w+)')
        return reg_exp.findall(name).pop()

def get_off_firstname(name):
    '''Parse the victim's last name'''
    non_player = ['No Player Victim', 'Team', 'Organization']
    if name in non_player:
        return None
    
    if ',' in name:
        reg_exp =  re.compile(r'\w+[,]?\s(\w+)')
        return reg_exp.findall(name).pop()
    
    else:
        reg_exp =  re.compile(r'(.*)\s\w+')
        return reg_exp.findall(name).pop()

def get_vic_lastname(name):
    '''Parse the victim's last name'''
    non_player = ['No Player Victim', 'Team', 'Organization']
    if name in non_player:
        return None
    
    if ',' in name:
        reg_exp =  re.compile(r'(\w+)[,]?\s\w+')
        return reg_exp.findall(name).pop()
    
    else:
        reg_exp =  re.compile(r'.*\s([A-Z].\w+|\w+)')
        return reg_exp.findall(name).pop()

def get_vic_firstname(name):
    non_player = ['No Player Victim', 'Team', 'Organization']
    if name in non_player:
        return None
    
    if ',' in name:
        reg_exp =  re.compile(r'\w+[,]?\s(\w+)')
        return reg_exp.findall(name).pop()
    
    else:
        reg_exp =  re.compile(r'(.*)\s\w+')
        return reg_exp.findall(name).pop()

# Apply functions to create new columns
dops['offense_cat'] = dops['offense'].apply(re_parse_offense)
dops['victim'] = dops['offense'].apply(re_parse_victim)
dops['total_susp_games'] = dops['susp'].apply(re_parse_total_games)
dops['playoff_susp_games'] = dops['susp'].apply(re_parse_playoff_games)
dops['preseason_susp_games'] = dops['susp'].apply(re_parse_preseason_games)
dops['reg_susp_games'] = (dops['total_susp_games'] - dops['playoff_susp_games']
                         - dops['preseason_susp_games'])
dops['forfeit_sal'] = dops['forfeit_sal'].apply(money_to_float)

# Turn dates into datetime, extract year, month, date
dops['off_date'] = pd.to_datetime(dops['off_date'], 
    infer_datetime_format=True)
dops['off_year'] = dops['off_date'].apply(get_year)
dops['off_month'] = dops['off_date'].apply(get_month)
dops['off_day'] = dops['off_date'].apply(get_day)

# Same as above but for the dops date
dops['dops_date'] = pd.to_datetime(dops['dops_date'], 
    infer_datetime_format=True)
dops['dops_year'] = dops['dops_date'].apply(get_year)
dops['dops_month'] = dops['dops_date'].apply(get_month)
dops['dops_day'] = dops['dops_date'].apply(get_day)

dops['off_last_name'] = dops['offender'].apply(get_off_lastname)
dops['off_first_name'] = dops['offender'].apply(get_off_firstname)
dops['vic_last_name'] = dops['victim'].apply(get_vic_lastname)
dops['vic_first_name'] = dops['victim'].apply(get_vic_firstname)

# Manually set some unique cases
dops.set_value(21, 'offense_cat', 'Spearing')
dops.set_value(139,'offense_cat', 'Instigating')
dops.set_value(147, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(198, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(205, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(248, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(338, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(339, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(352, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(381, 'offense_cat', 'Illegal Hit')
dops.set_value(388, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(390, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(394, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(401, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(431, 'offense_cat', 'Inappropriate Conduct')
dops.set_value(182, 'total_susp_games', 6)
dops.set_value(241, 'total_susp_games', 6)
dops.set_value(381, 'total_susp_games', 4)
dops.set_value(94, 'forfeit_sal', 0)

dops.drop(dops.index[1], inplace=True) # Suspension included in two data sets


dops.to_csv('Scrubbed_CSV.csv')
