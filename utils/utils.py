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
    max_message_length = len(f"Waiting {seconds} seconds for page to load...")

    for remaining in range(seconds, 0, -1):
        message = f"Waiting {remaining} seconds for page to load..."
        # Pad the message to match the maximum length, ensuring no leftover characters
        sys.stdout.write(f"\r{message}{' ' * (max_message_length - len(message))}")
        sys.stdout.flush()
        time.sleep(1)
    
    # Final message after countdown ends
    final_message = f"Waited {seconds} seconds to load"
    sys.stdout.write(f"\r{final_message}{' ' * (max_message_length - len(final_message))}\n")
    sys.stdout.flush()


def scroll_to_bottom(driver, scroll_pause_time=5):
    """Scroll to the bottom of the page to load dynamic content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for the page to load
        time.sleep(scroll_pause_time)
        
        # Calculate new scroll height and compare with the last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


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
            
            # Optional initial wait
            countdown_timer(wait_time)

            # Scroll to the bottom of the page
            scroll_to_bottom(driver)

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


def load_yaml(file_path):
    """Load configuration values from a YAML file."""

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"{bcolors.FAIL}Configuration file '{file_path}' not found. Using default values.{bcolors.ENDC}")
        config = {}

    return config


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


misconduct = {
    'send off': [
        'violent conduct',
        'serious foul play',
        'second yellow'
        ],
    'caution': [
        'unsporting behavior',
        'poor sportsmanship',
        'foul'
    ]
}
