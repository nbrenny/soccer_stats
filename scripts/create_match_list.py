from utils.utils import get_soup
import argparse
import re
import os
from utils.utils import save_to_json, save_to_yaml
import yaml
import sys


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create url list')
    parser.add_argument('-c', '--config', help='config file', required=True)
    parser.add_argument('-w', '--wait', help='Overriden default wait time [seconds]', required=False, default=None, type=int)
    args = vars(parser.parse_args(args))
    return args


def load_config_from_yaml(file_path):
    """Load configuration values from a YAML file."""
    # Default values if the YAML file or keys are not provided
    default_config = {
        'url': None,
        'outfile': './match_details.json',
        'wait_time': 5,
        'dir': 'unknown'
    }

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Configuration file '{file_path}' not found. Using default values.")
        config = {}

    # Merge with default values (YAML config overwrites defaults if keys are present)
    config = {**default_config, **config}

    # Check for required fields (in this case, 'url' is required)
    if config['url'] is None:
        raise ValueError("The 'url' field is required in the YAML configuration.")

    return config



def query(soup, class_='mls-c-schedule__matches'):
    # select the main div containing the matches
    matches_div = soup.find('div', class_=class_)

    return matches_div


def get_date(match_container):
    date_div = match_container.parent.parent.find_all('div', string=re.compile(r'^(?:\w+, )?(?:\w+ )?\w+ \d+$'))
    date_text=None
    to_remove = ['Monday ','Tuesday ','Wednesday ','Thursday ','Friday ','Saturday ','Sunday ','Tomorrow, ','Yesterday, ']
    for da in date_div:
        date_text = da.text.strip()
        for el in to_remove:
            if el in date_text:
                date_text=date_text.replace(el,'')
    if date_text:
        return date_text
    else:
        print('NO DATE FOUND')


def get_link(match_info,match_container):
    match_link = match_container.find('a')['href']
    match_info['match_link'] = match_link+'/feed'

    return match_info


def get_teams(match_info,match_container):
    for t in ['home','away']:
        team = match_container.find('div', class_=re.compile(f'mls-c-club --{t}'))
        match_info[t]['abbreviation'] = team.find('span', class_=re.compile('mls-c-club__abbreviation')).text.strip()
        match_info[t]['name'] = team.find('span', class_=re.compile('mls-c-club__shortname')).text.strip()

    return match_info


def get_scores(match_info,match_container):
    scores = match_container.find_all('span', class_='mls-c-scorebug__score')
    for i,t in enumerate(['home','away']):
        match_info[t]['score'] = scores[i].text.strip() if scores else None

    return match_info


def extract(matches_div):
    match_data = {}
    for match_container in matches_div.find_all('div', class_='mls-c-match-list__match-container'):
        match_info = {'home':{},'away':{}}
        match_info=get_link(match_info,match_container)
        match_info=get_teams(match_info,match_container)
        match_info=get_scores(match_info,match_container)
        match_data[f'{match_info["home"]["name"]} vs. {match_info["away"]["name"]} ({get_date(match_container)})'] = match_info

    return match_data


def main(args):
    args=parse_args(args)
    config=load_config_from_yaml(args['config'])
    soup=get_soup(config['url'],wait_time=args['wait']) if args['wait'] else get_soup(config['url'],wait_time=config['wait_time'])
    matches_div=query(soup)
    match_data=extract(matches_div)
    json_filename = config['dir']+'/'+config['outfile']
    save_to_json(match_data,json_filename)
    config['saved_match_list_json'] = json_filename
    save_to_yaml(config,args['config'],printout=False)
    #print(f"\n\n{config['dir']}")


if __name__=="__main__":
    main(sys.argv[1:])