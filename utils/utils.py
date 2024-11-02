import json
import yaml
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.params import params
import sys
import time


def ensure_directory_exists(filepath):
    """Check if the directory for the given filepath exists, and create it if it does not."""
    directory = os.path.dirname(filepath)  # Get the directory from the file path
    
    if (not os.path.exists(directory)):  # Check if the directory exists
        if directory: # non-home directories only
            os.makedirs(directory)  # Create the directory and any intermediate directories
            print(f'Directory created: {directory}')


def save_to_json(dic,outfile,printout=True):
    ensure_directory_exists(outfile)
    with open(outfile, 'w') as f:
        json.dump(dic,f,indent=2)
    if printout:
        print(f'\nsaved json to {outfile}\n')


def read_json(filepath):
    with open(filepath, 'r') as f:
        dic = json.load(f)
    return dic


def save_to_yaml(dic,outfile,printout=True):
    ensure_directory_exists(outfile)
    with open(outfile, 'w') as f:
        yaml.dump(dic,f,indent=2)
    if printout: 
        print(f'\nsaved yaml to {outfile}\n')


def get_analysis_dir():
    return os.environ[params['analysis_dir']]


def countdown_timer(seconds):
    print('')
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rWaiting {remaining} seconds for page to load...")
        sys.stdout.flush()
        time.sleep(1)
    print("\rPage loaded!")


def get_soup(url, use_selenium=True, wait_time=5):
    if use_selenium:
        try:
            # Set up Chrome options for headless mode
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")  # Recommended for running in containers
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            
            # Initialize the WebDriver with Chrome options
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            countdown_timer(wait_time)

            # Get the page source after JS has rendered
            html = driver.page_source
            driver.quit()

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
        
        except Exception as e:
            sys.exit(f"Failed to retrieve the page using Selenium: {e}")
    
    else:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
        else:
            sys.exit("Failed to retrieve the page using requests.")
    
    print(f'Loaded page {url}')
    return soup


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'