import json
from jinja2 import Environment, FileSystemLoader
import argparse
import sys
from utils.utils import load_yaml, bcolors
import os
from datetime import datetime


def parse_args(args):
    parser = argparse.ArgumentParser(description="Generate HTML from JSON input using a Jinja2 template.")
    parser.add_argument('-t', '--template', required=False, help="Path to the Jinja2 HTML template file.",default=None)
    parser.add_argument('-i', '--input', required=False, help="Path to the input JSON file.",default=None)
    parser.add_argument('-o', '--output_dir', required=False, help="Path to the output HTML file.",default=None)
    parser.add_argument('-d', '--date', required=False, help="Date for the week's page (format: YYYY-MM-DD).")
    parser.add_argument('-c', '--config', help="Path to a JSON configuration file.", default=None)
    
    return vars(parser.parse_args(args))


def get_all_dates(output_dir):
    """
    Scan the output directory to find all existing weekly pages (dates).
    Returns a sorted list of dates in YYYY-MM-DD format.
    """
    dates = []
    for filename in os.listdir(output_dir):
        if filename.endswith('.html') and filename != "index.html":
            date_str = filename.replace('.html', '')
            try:
                # Validate the date format
                datetime.strptime(date_str, '%Y-%m-%d')
                dates.append(date_str)
            except ValueError:
                pass  # Skip files that don't match the date format
    return sorted(dates)


def generate_html(input, template, output_dir, date, all_dates):
    """
    Generate a weekly HTML file from JSON input and update the main page with navigation.
    """
    # Load the JSON file
    with open(input, 'r') as f:
        data = json.load(f)

    # Process the data
    matches = []
    red_cards = []

    for match_name, details in data.items():
        url = details["url"]
        misconduct = details["misconduct"]["misconduct"]
        yellow_count = misconduct["yellow cards"]["n_yellow_cards"]
        red_count = misconduct["red cards"]["n_red_cards"]

        # Add match summary
        matches.append({
            "name": match_name,
            "url": url,
            "yellow_cards": yellow_count,
            "red_cards": red_count,
        })

        # Add red card details
        if red_count > 0:
            for i in range(1, red_count + 1):
                red_card = misconduct["red cards"].get(f"red_card_{i}")
                if red_card:
                    red_cards.append({
                        "player": red_card["player"],
                        "description": red_card["description"],
                        "minute": red_card["minute"],
                        "club": red_card["club"],
                        "url": url,
                    })

    # Render the HTML for the week
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)
    output = template.render(matches=matches, red_cards=red_cards, date=date, all_dates=all_dates)

    # Save the weekly HTML
    week_output_path = os.path.join(output_dir, f"{date}.html")
    with open(week_output_path, 'w') as f:
        f.write(output)
    print(f"Weekly HTML generated as '{week_output_path}'")

    # Update main navigation
    update_main_page(output_dir, date)


def update_main_page(output_dir, new_date, main_template='webpage/config/html/main_template.html'):
    """
    Update the main navigation page with links to all weekly pages.
    """
    # Gather all weekly pages
    pages = [
        f.replace('.html', '') for f in os.listdir(output_dir) if f.endswith('.html') and f != "index.html"
    ]
    pages.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'))  # Sort by date

    # Group pages by month
    grouped_pages = {}
    for page in pages:
        month = datetime.strptime(page, '%Y-%m-%d').strftime('%B %Y')
        grouped_pages.setdefault(month, []).append(page)

    # Render the main page
    env = Environment(loader=FileSystemLoader('.'))
    main_template = env.get_template(main_template)
    output = main_template.render(grouped_pages=grouped_pages)

    # Save the main page
    main_page_path = os.path.join(output_dir, 'index.html')
    with open(main_page_path, 'w') as f:
        f.write(output)
    print(f"Main navigation updated as '{main_page_path}'")


def main(args=None):
    """
    Entry point for the script. Parses arguments and calls generate_html.
    """
    args=parse_args(args)
    if args['config']:
        config = load_yaml(args['config'])

        # check if other command line args are also provided
        if any(args[key] for key in config):
            sys.exit(f'{bcolors.FAIL}Provide only one of a config file or command line arguments for input,template,output!{bcolors.FAIL}')
        
        # Gather all existing dates
        all_dates = get_all_dates(config['output_dir'])
        # Add the new date to the list if not already present
        if config['date'] not in all_dates:
            all_dates.append(config['date'])
            all_dates.sort()  # Ensure dates remain sorted

        generate_html(all_dates=all_dates,**config)

    else:
        # Gather all existing dates
        all_dates = get_all_dates(config['output_dir'])
        # Add the new date to the list if not already present
        if config['date'] not in all_dates:
            all_dates.append(config['date'])
            all_dates.sort()  # Ensure dates remain sorted
        generate_html(all_dates=all_dates,**args)


if __name__ == "__main__":
    main(sys.argv[1:])