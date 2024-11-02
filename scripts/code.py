import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse
import sys
import time
import re
from utils.utils import read_json, bcolors, get_soup, save_to_json



# TO DO 
# - have get_inputs return a dictionary that contains the score and title of the match
# - have query save to a dictionary of the same structure

def parse_args():
    parser = argparse.ArgumentParser(description='Check MLS match')
    parser.add_argument('-u', '--url', help='URL to match', required=False, default=None)
    parser.add_argument('-w', '--wait_time', help='Wait time', required=False, default=5, type=int)
    parser.add_argument('-i', '--input_json', help='Input json of URLs to check', required=False, default=None)
    parser.add_argument('-o', '--output_json', help='Output json with stats', required=False, default=None)
    parser.add_argument('--no_selenium', help='Don\'t use selenium', required=False, default=False, action='store_true')
    args = vars(parser.parse_args())
    return args


def check_inputs(args):
    if ((not args['url']) and (not args['input_json'])):
        print(f'{bcolors.FAIL}[ERROR] Neither url nor json provided. Must provide one URL input type!{bcolors.ENDC}')
        sys.exit()
    elif (args['url'] and args['input_json']):
        print(f'{bcolors.WARNING}[WARNING] Both url and json provided. Are you sure this is what you want to do?{bcolors.ENDC}')


def get_inputs(url,input_json):
    url_list = []
    if url: 
        url_list.append(url)
    if input_json:
        input_dict = read_json(input_json)
        input_urls = [input_dict[key]['match_link'] for key in input_dict]
        url_list+=input_urls
    return url_list


def query(soup):
    red_card_events = []

    # Find all red card commentary elements
    red_card_elements = soup.find_all(class_="mls-o-match-feed__commentary--red-card")
    
    for red_card in red_card_elements:
        event_data = {}
        
        # Extract the minute of the event
        minute_tag = red_card.find(class_="mls-o-match-feed__minute")
        event_data["minute"] = minute_tag.get_text(strip=True) if minute_tag else "N/A"
        
        # Extract the description or body of the event
        body_tag = red_card.find(class_="mls-o-match-feed__body--no-video")
        event_data["description"] = body_tag.get_text(strip=True) if body_tag else "N/A"
        
        # Add the structured event data to the list
        red_card_events.append(event_data)
    
    # Print or process the list of red card events
    if red_card_events:
        print("Red card events found:")
        for event in red_card_events:
            print(event)
    else:
        print("No red card events found in the match.")
    
    return red_card_events


def main():
    # Parse arguments
    args = parse_args()
    check_inputs(args)
    url = args['url']
    input_json = args['input_json']
    output_json = args['output_json']
    selenium = args['no_selenium']
    wait_time = args['wait_time']

    matches={}
    for URL in get_inputs(url,input_json):
        soup = get_soup(URL, use_selenium=not selenium, wait_time=wait_time)
        matches[URL] = query(soup)  

    save_to_json(matches,output_json)

if __name__ == "__main__":
    main()