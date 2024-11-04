from bs4 import BeautifulSoup


def red_cards(soup: BeautifulSoup) -> dict:
    red_card_information = {}

    # Find all red card commentary elements
    red_card_elements = soup.find_all(class_="mls-o-match-feed__commentary--red-card")
    red_card_information['n_red_cards'] = len(red_card_elements)
    for i,red_card in enumerate(red_card_elements):
        event_data = {}
        
        # Extract the minute of the event
        minute_tag = red_card.find(class_="mls-o-match-feed__minute")
        event_data["minute"] = minute_tag.get_text(strip=True) if minute_tag else "N/A"
        
        # Extract player and club 
        player_tag = red_card.find(class_="mls-o-player-block__player-info")
        name_tag = player_tag.find(class_="mls-o-player-block__player-name")
        event_data["player"] = name_tag.get_text(strip=True) if name_tag else "N/A"
        details_tag = player_tag.find(class_="mls-o-player-block__club-abbreviation")
        event_data["club"] = details_tag.get_text(strip=True) if details_tag else "N/A"

        # Extract the description 
        description = red_card.find(class_="mls-o-match-feed__body--no-video")
        event_data["description"] = description.get_text(strip=True) if description else "N/A"
        
        # Add the structured event data to the list
        red_card_information[f'red_card_{i}']=event_data

    return red_card_information


def yellow_cards(soup: BeautifulSoup) -> dict:
    yellow_card_information = {}

    # Find all yellow card commentary elements
    yellow_card_elements = soup.find_all(class_="mls-o-match-feed__commentary--yellow-card")
    yellow_card_information['n_yellow_cards'] = len(yellow_card_elements)
    for i,yellow_card in enumerate(yellow_card_elements):
        event_data = {}
        
        # Extract the minute of the event
        minute_tag = yellow_card.find(class_="mls-o-match-feed__minute")
        event_data["minute"] = minute_tag.get_text(strip=True) if minute_tag else "N/A"

        # Extract the description and related information
        description = yellow_card.find(class_="mls-o-match-feed__comment")
        description_string = description.get_text(strip=True) if description else "N/A"
        partitioned_description_string = description_string.partition('(')
        event_data["description"] = description_string
        event_data["name"] = partitioned_description_string[0]
        event_data["club"] = partitioned_description_string[-1].partition(')')[0]
        
        # Add the structured event data to the list
        yellow_card_information[f'yellow_card_{i}']=event_data

    return yellow_card_information


def misconduct(soup: BeautifulSoup) -> dict:
    misconduct_information = {}
    misconduct_information['red cards'] = red_cards(soup)
    misconduct_information['yellow cards'] = yellow_cards(soup)

    return misconduct_information