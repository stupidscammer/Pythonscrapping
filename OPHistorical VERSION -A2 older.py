# -*- coding: utf-8 -*-
import os
import re
import csv
import math
import json
import time
import random
import urllib
import codecs
import requests
import datetime
from lxml.html import fromstring

############### PROGRAM SETTINGS ####################

USERNAME = 'LuisFael'

PASSWORD = '173f0365'

INPUT_FILE = 'LeagueLinks.txt'

OUTPUT_FILE = 'HistoricalMatches.csv'

############### PROGRAM SETTINGS ####################

LIST_OF_SIZES = {
    '1X2FT':[3,3],
    '1X21H':[3,3],
    'AHFT':[66,2],
    'OUFT':[14,2],
    'OU1H':[6,2],
    'CSFT':[16,1],
    'BTSFT':[2,2],
    'DCFT':[3,3],
    'DNBFT':[2,2],
    }

LIST_OF_BOOKIES = {
    'betfair':'44',
    'matchbook':'390',
    'smarkets':'485',
    'bet365':'16',
    }

LIST_OF_ODDS = {
    '1X2FT':'1-2',
    '1X21H':'1-3',
    'AHFT':'5-2',
    'OUFT':'2-2',
    'OU1H':'2-3',
    'CSFT':'8-2',
    'BTSFT':'13-2',
    'DCFT':'4-2',
    'DNBFT':'6-2',
    }

LOOKUP = {
    '1X2FT':['E-1-2-0-0-0'],
    '1X21H':['E-1-3-0-0-0'],

    'AHFT':['E-5-2-0--4-0',
            'E-5-2-0--3.75-0', 'E-5-2-0--3.5-0', 'E-5-2-0--3.25-0', 'E-5-2-0--3-0',
            'E-5-2-0--2.75-0', 'E-5-2-0--2.5-0', 'E-5-2-0--2.25-0', 'E-5-2-0--2-0',
            'E-5-2-0--1.75-0', 'E-5-2-0--1.5-0', 'E-5-2-0--1.25-0', 'E-5-2-0--1-0',
            'E-5-2-0--0.75-0', 'E-5-2-0--0.5-0', 'E-5-2-0--0.25-0', 'E-5-2-0-0-0',
            'E-5-2-0-0.25-0', 'E-5-2-0-0.5-0', 'E-5-2-0-0.75-0', 'E-5-2-0-1-0',
            'E-5-2-0-1.25-0', 'E-5-2-0-1.5-0', 'E-5-2-0-1.75-0', 'E-5-2-0-2-0',
            'E-5-2-0-2.25-0', 'E-5-2-0-2.5-0', 'E-5-2-0-2.75-0', 'E-5-2-0-3-0',
            'E-5-2-0-3.25-0', 'E-5-2-0-3.5-0', 'E-5-2-0-3.75-0', 'E-5-2-0-4-0',
            ],
    
    'OUFT':['E-2-2-0-0.5-0', 'E-2-2-0-1.5-0', 'E-2-2-0-2.5-0', 'E-2-2-0-3.5-0', 'E-2-2-0-4.5-0', 'E-2-2-0-5.5-0', 'E-2-2-0-6.5-0'],
    'OU1H':['E-2-3-0-0.5-0', 'E-2-3-0-1.5-0', 'E-2-3-0-2.5-0'],

    'CSFT':['E-8-2-0-0-2', 'E-8-2-0-0-5', 'E-8-2-0-0-6', 'E-8-2-0-0-10', 'E-8-2-0-0-11', 'E-8-2-0-0-12',
            'E-8-2-0-0-1', 'E-8-2-0-0-3', 'E-8-2-0-0-7', 'E-8-2-0-0-13',
            'E-8-2-0-0-4', 'E-8-2-0-0-9', 'E-8-2-0-0-8', 'E-8-2-0-0-16', 'E-8-2-0-0-15', 'E-8-2-0-0-14'],
    
    'BTSFT':['E-13-2-0-0-0'],

    'DCFT':['E-4-2-0-0-0'],

    'DNBFT':['E-6-2-0-0-0'],
    }

def SaveCSVData(INFO,MODE='a'):
    global OUTPUT_FILE

    try:
        with open(OUTPUT_FILE, MODE, encoding='utf-8-sig', newline='\n') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(INFO)
            
    except Exception as e:
        print (f'\n # CSV FILE ERROR: {e}\n')

def GetWebPage(url,payload=None,path=None):
    global SESSION
    global REQUEST_COUNTER
    
    try:
        if not path or not os.path.isfile(path):

            REQUEST_COUNTER += 1

            if REQUEST_COUNTER%2 == 0:
                time.sleep(1)
                
            SESSION.headers.update({'host': urllib.parse.urlsplit(url).hostname})

            if payload:
                response = SESSION.post(url, data=payload, timeout=60)
            else:
                response = SESSION.get(url, timeout=60)

            if response.status_code != 200:

                if response.status_code == 404 or response.status_code == 410:
                    return None

                raise Exception
            
            response = response.text

            if path:
                codecs.open(path,'w','utf-8').write(response)
        else:
            response = codecs.open(path,'r','utf-8').read()
            
    except:
        time.sleep(random.randint(2,3))

        return GetWebPage(url,payload,path)
    
    return response

def GetOdds(odds_url,odds_type,odds_slug):
    
    odds, size = {}, LIST_OF_SIZES[odds_type][0]

    for bookie in LIST_OF_BOOKIES.keys():

        odds[bookie] = {
            'back' : {'openingOdd':['']*size, 'odds':['']*size},
            'lay' : {'openingOdd':['']*size, 'odds':['']*size},
            }

    odds_path = f'Oddsportal/{odds_slug}-{odds_type}.html'

    response = GetWebPage(odds_url, None, odds_path)

    try:
        content = json.loads(re.search(".dat', (.+?)\)\;",response).group(1))
    except:
        try:
            content = json.loads(response)
        except:
            os.remove(odds_path)
            return [odds,False]
        
    index = -1

    for key in LOOKUP[odds_type]:

        if index < 0:
            index = 0
        else:
            index += LIST_OF_SIZES[odds_type][1]

        for skey in ['back','lay']:
            
            try:
                if not key in content['d']['oddsdata'][skey].keys():
                    continue
            except:
                continue

            section = content['d']['oddsdata'][skey][key]

            for tp in ['openingOdd','odds']:
                    
                if not tp in section.keys():
                    continue

                for bookie in LIST_OF_BOOKIES.keys():

                    bookcode = LIST_OF_BOOKIES[bookie]

                    if not bookcode in section[tp].keys():
                        continue

                    odds_ds = section[tp][bookcode]

                    try:
                        if type(odds_ds) == dict:
                        
                            if odds_type in ['1X2FT','1X21H','DCFT']:
                                ds = [round(odds_ds['0'],2),round(odds_ds['1'],2),round(odds_ds['2'],2)]
                            elif odds_type in ['AHFT','OUFT','OU1H','BTSFT','DNBFT']:
                                ds = [round(odds_ds['0'],2),round(odds_ds['1'],2)]
                            elif odds_type in ['CSFT']:
                                ds = [round(odds_ds['0'],2)]

                        elif type(odds_ds) == list:
                            
                            if odds_type in ['1X2FT','1X21H','DCFT']:
                                ds = [round(odds_ds[0],2),round(odds_ds[1],2),round(odds_ds[2],2)]
                            elif odds_type in ['AHFT','OUFT','OU1H','BTSFT','DNBFT']:
                                ds = [round(odds_ds[0],2),round(odds_ds[1],2)]
                            elif odds_type in ['CSFT']:
                                ds = [round(odds_ds[0],2)]

                        else:
                            continue
                    except:
                        continue

                    for i in range(len(ds)):
                        odds[bookie][skey][tp][index+i] = ds[i]

    return [odds,True]

def GetMatchOdds(league,season,match_url):

    match_slug = [s.strip() for s in match_url.split('/') if s.strip()][-1]

    match_path = f'Oddsportal/{league}/{season}/Matches/{match_slug}.html'

    response = GetWebPage(match_url, None, match_path)
    
    try:
        content = re.search('\<Event \:data\="(.+?)"',response).group(1).replace('&quot;','"')

        event = json.loads(content)['eventData']

        m_id, m_hash, m_hash_f = event['id'], urllib.parse.unquote(event['xhash']), urllib.parse.unquote(event['xhashf'])
    except:
        return None
    
    odds_slug = f'{league}/{season}/Matches/{match_slug}'

    match_odds = {}

    for odd in LIST_OF_ODDS.keys():

        o_id = LIST_OF_ODDS[odd]

        #m_ts = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()*1000)

        #odds_url = f'https://fb.oddsportal.com/feed/match/1-1-{m_id}-{o_id}-{m_hash_f}.dat?={m_ts}'
        odds_url = f'https://www.oddsportal.com/feed/match-event/1-1-{m_id}-{o_id}-{m_hash_f}.dat'

        odds = GetOdds(odds_url, odd, odds_slug)

        if not odds[1]:

            #odds_url = f'https://fb.oddsportal.com/feed/match/1-1-{m_id}-{o_id}-{m_hash}.dat?={m_ts}'
            odds_url = f'https://www.oddsportal.com/feed/match-event/1-1-{m_id}-{o_id}-{m_hash}.dat'

            odds = GetOdds(odds_url, odd, odds_slug)
            
        match_odds[odd] = odds[0]
        
    return match_odds

def GetSeasonData(league,season,season_key,page=1):

    page_path = f'Oddsportal/{league}/{season}/{season}-{page}.html'
    
    page_url = f'https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{season_key}/X0/1/0/page/{page}/'

    response = GetWebPage(page_url, None, page_path)

    try:
        content = json.loads(response)

        num_of_pages = int(math.ceil(content['d']['total']/content['d']['onePage']))

        results = content['d']['rows']
    except:
        return True #None

    title = f"{results[0]['country-name']} - {results[0]['tournament-name']}"

    for row in results[:]:

        try:
            mdt = datetime.datetime.utcfromtimestamp(row['date-start-timestamp'])

            if mdt.date() < end_date:
                return False

            ht, at = row['home-name'], row['away-name']

            try:
                ft_score = row['result']

                if type(ft_score) == str:
                    ft_score = f'"{ft_score}"'
            except:
                ft_score = ''
                
            try:
                h1_score = row['partialresult'].split(',')[0].strip()
                h2_score = row['partialresult'].split(',')[1].strip()

                if type(h1_score) == str:
                    h1_score = f'"{h1_score}"'

                if type(h2_score) == str:
                    h2_score = f'"{h2_score}"'
            except:
                h1_score, h2_score = '',''
                
            mdt = mdt.strftime('%Y-%m-%d %H:%M:%S')

            match_url = urllib.parse.urljoin('https://www.oddsportal.com/', row['url'])
                    
            print ('\t\t #', ht, ' - ', at)

            match_odds = GetMatchOdds(league, season, match_url)

            if not match_odds:
                continue

            for book in LIST_OF_BOOKIES.keys():

                if book in ['betfair','matchbook','smarkets']:
                    skey_list = ['back','lay']
                else:
                    skey_list = ['back']

                for skey in skey_list:

                    for tp in ['openingOdd','odds']:

                        odds = []

                        #for key in ['1X2FT','1X21H','AHFT','OUFT','OU1H','CSFT','BTSFT','DCFT','DNBFT']:
                        for key in ['1X2FT','1X21H','OUFT','OU1H','BTSFT','DCFT']:

                            odds += match_odds[key][book][skey][tp]

                        if tp == 'openingOdd':
                            SaveCSVData([match_url,title,season,mdt,ht,at,ft_score,h1_score,h2_score,book,skey,'opening']+odds)
                            
                        else:
                            SaveCSVData([match_url,title,season,mdt,ht,at,ft_score,h1_score,h2_score,book,skey,'closing']+odds)
        except:
            continue
        
    if page < num_of_pages:
        
        return GetSeasonData(league,season,season_key,page+1)

    return True
        
def GetHistoricalData(league_url):

    slug = [s.strip().title() for s in league_url.split('/') if s.strip()]

    league = f'{slug[-3]}-{slug[-2]}'

    for s in ['\\','/',':','*','?','"','<','>','|']:
        league = league.replace(s,' ')

    league_path = f'Oddsportal/{league}.html'

    response = GetWebPage(league_url, None, league_path)

    html = fromstring(response)

    print ('\n #', league)

    for season in html.xpath('//div/a[contains(@href,"/results/")]')[:]:

        season_url = season.get('href')

        season = season.text_content().strip().replace('/','-')

        print ('\n\t #',season)

        if not os.path.exists(f'Oddsportal/{league}/{season}/Matches/'):
            os.makedirs(f'Oddsportal/{league}/{season}/Matches/')
        
        season_path = f'Oddsportal/{league}/{season}/{season}.html'

        response = GetWebPage(season_url, None, season_path)

        try:
            content = re.search('\:odds\-request="(.+?)"',response).group(1).replace('&quot;','"')

            season_url = json.loads(content)['url'].split('?')[0]

            season_key = re.search('\/ajax\-sport\-country\-tournament\-archive_\/1\/(.+?)\/',season_url).group(1)

            if not season_key:
                raise Exception
        except:
            continue

        if not GetSeasonData(league, season, season_key):
            break
        
def LoginOddsportal():

    endpoint = 'https://www.oddsportal.com/login/'

    response = GetWebPage(endpoint, None, None)

    html = fromstring(response)

    TOKEN = html.xpath('//input[@name="_token"]')[0].get('value')
    
    payload = {
        '_token': TOKEN,
        'referer': 'https://www.oddsportal.com/',
        'login-username': USERNAME,
        'login-password': PASSWORD,
        'login-stay-signed': 1,
        'login-submit': 'Login'
        }

    endpoint = 'https://www.oddsportal.com/userLogin'

    GetWebPage(endpoint, payload, None)
    
if __name__=="__main__":

    try:
        print (f'\n ############### Oddsportal.com Scraper ###############')

        if not os.path.exists('Oddsportal'):
            os.makedirs('Oddsportal')
            
        REQUEST_COUNTER = 0
        SESSION = requests.Session()
        SESSION.headers.update({'x-requested-with': 'XMLHttpRequest'})
        SESSION.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
        SESSION.headers.update({'referer': 'https://www.oddsportal.com/'})
        
        LIST_OF_LEAGUES = []

        with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
            
            for row in f.readlines():
                print("current website is:",row)
                if not row.strip() or not 'www.oddsportal.com' in row:
                    continue
                
                if '/results' in row:
                    row = row.split('/results')[0]

                if not row[-1]=='/':
                    row += '/'

                row = urllib.parse.urljoin(row,'results')

                LIST_OF_LEAGUES += [row.strip()]

        end_date = input ('\n # Enter End Date (d/m/yy) (Default = 1/11/21): ').strip()

        if not end_date:
            end_date = '1/11/21'
            
        try:
            end_date = datetime.datetime.strptime(end_date, "%d/%m/%y").date()

            today_date = datetime.datetime.now().date()

            if end_date >= today_date:
                raise Exception
        except:
            raise Exception ('Input Date Must be Before Today and in Correct Format.')

        HEADERS = ['URL','League','Season','Date/Time','Home','Away','FT','1st Half','2nd Half','Bookmaker','B/L','O/C']
        HEADERS += ['1X2FT 1','1X2FT X','1X2FT 2','1X21H 1','1X21H X','1X21H 2']

        #for s in ['0.25','0.5','0.75','1','1.25','1.5','1.75','2','2.25','2.5','2.75','3','3.25','3.5','3.75','4'][::-1]:
            #HEADERS += [f'AHFT-{s} 1']
            #HEADERS += [f'AHFT-{s} 2']

        #for s in ['0','0.25','0.5','0.75','1','1.25','1.5','1.75','2','2.25','2.5','2.75','3','3.25','3.5','3.75','4']:
            #HEADERS += [f'AHFT{s} 1']
            #HEADERS += [f'AHFT{s} 2']
        
        for s in ['0.5','1.5','2.5','3.5','4.5','5.5','6.5']:
            HEADERS += [f'OUFT{s} OV']
            HEADERS += [f'OUFT{s} UN']

        for s in ['0.5','1.5','2.5']:
            HEADERS += [f'OU1H{s} OV']
            HEADERS += [f'OU1H{s} UN']

        #for s in ['1:0','2:0','2:1','3:0','3:1','3:2','0:0','1:1','2:2','3:3','0:1','0:2','1:2','0:3','1:3','2:3']:
            #HEADERS += [f'CSFT {s}']

        HEADERS += ['BTTSFT Y','BTTSFT N','DCFT 1X','DCFT 12','DCFT 2X']
        #HEADERS += ['DNBFT 1','DNBFT 2']

        OUTPUT_FILE = OUTPUT_FILE.rsplit('.csv',1)[0] + ' (' + datetime.datetime.now().strftime("%m-%d-%Y %I.%M %p") + ').csv'

        SaveCSVData(HEADERS,'w')

        print ('\n - Collecting Historical Odds from Oddsportal..')

        LoginOddsportal()

        for url in LIST_OF_LEAGUES[:]:

            try:
                GetHistoricalData(url)
            except:
                continue

        print ('\n - Saving Output to CSV File..')
        
    except Exception as e:
        print (f'\n # FATAL ERROR: {e}')
        
    print (f'\n ######################################################')

    input ('\n Press any Key to Exit..')
# directory = os.getcwd()

# print(directory)