import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse
import sys
import time
import re
from utils.utils import read_json, bcolors, get_soup, save_to_json, load_yaml
import get_stats
import os


# TO DO 
# - have query save to a dictionary of the same structure

def parse_args():
    parser = argparse.ArgumentParser(description='Check MLS match')
    parser.add_argument('-u', '--url', help='URL to match', required=False, default=None)
    parser.add_argument('-w', '--wait_time', help='Wait time', required=False, default=5, type=int)
    parser.add_argument('-c', '--config', help='Config file', required=False, default=None)
    parser.add_argument('-i', '--input_json', help='Input json of URLs to check', required=False, default=None)
    parser.add_argument('-o', '--output_json', help='Output json with stats', required=False, default=None)
    parser.add_argument('--no_selenium', help='Don\'t use selenium', required=False, default=False, action='store_true')
    args = vars(parser.parse_args())
    return args


def check_inputs(args):
    if ((not args['url']) and (not args['input_json']) and (not args['config'])):
        print(f'{bcolors.FAIL}[ERROR] Neither url nor json nor config provided. Must provide one URL input type!{bcolors.ENDC}')
        sys.exit()
    elif sum([bool(args['url']), bool(args['input_json']), bool(args['config'])])>1:
        print(f'{bcolors.WARNING}[WARNING] More than one input type provided. Are you sure this is what you want to do?{bcolors.ENDC}')


def get_inputs(url,input_json):
    url_dic = {}
    if url: 
        url_dic['unknown match'] = {'url': url}
    if input_json:
        input_dict = read_json(input_json)
        for key in input_dict.keys():
            url_dic[key] = {'url': input_dict[key]['match_link']}
    return url_dic


def query(soup):
    return_dict = {}
    return_dict['misconduct'] = get_stats.misconduct(soup)
    return return_dict


def main():
    # Parse arguments
    args = parse_args()
    check_inputs(args)
    url = args['url']
    config = args['config']
    if args['config']:
        config = load_yaml(args['config'])

    input_json = config['saved_match_list_json'] if config else args['input_json']
    output_json = os.path.dirname(input_json)+'/stats.json' if (config or input_json) else args['output_json']
    selenium = args['no_selenium']
    wait_time = args['wait_time']

    matches={}
    di = get_inputs(url,input_json)
    for key in di.keys():
        URL=di[key]['url']
        soup = get_soup(URL, use_selenium=not selenium, wait_time=wait_time)
        matches[key] = {'url':di[key]['url'],'misconduct':query(soup)}

    save_to_json(matches,output_json)

if __name__ == "__main__":
    main()