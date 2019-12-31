# Standard library imports
import json
import shutil
import os
import logging
import time #converting strings to dates

# Third party imports
from bs4 import BeautifulSoup
import requests

# Local application imports
import cars


def delete_all_files():
    # delete car folders
    shutil.rmtree("images", ignore_errors=True)
    # delete pickle files
    top = os.getcwd()
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            if(name.endswith(".json")):
                os.remove(os.path.join(root, name))
                logging.info('Deleted %s', name)


def should_download_images():
    try:
        with open('resources/last_modified_date.json', 'r') as read_file:
            last_updated_date = json.load(read_file)
        
        last_modified_date = get_last_modified_date()
        if last_modified_date != last_updated_date:
            delete_all_files()
            write_file = open('resources/last_modified_date.json', 'w')
            json.dump(last_modified_date, write_file)
            write_file.close()
            return True
        else:
            return False
    except FileNotFoundError:
        last_modified_date = get_last_modified_date()
        create_folder('resources')
        with open('resources/last_modified_date.json', 'w') as write_file:
            json.dump(last_modified_date, write_file)
            return True
    except Exception as e:
        logging.error(
            "Unable to determine last date website was updated. Error Message: %s", str(e))
        return False


# Get the date the website was last modified
def get_last_modified_date():
    # Get Date from Site Map Index XML
    xml_site_map_request = requests.get('http://www.dashboard-light.com/sitemap_index.xml')
    xml_site_map_soup = BeautifulSoup(xml_site_map_request.text, "html.parser")
    xml_site_map_last_mod = xml_site_map_soup.lastmod.string[:10]
    # Get Date from the Rankings Page
    rankings_request = requests.get('http://dashboard-light.com/rankings.html')
    rankings_soup = BeautifulSoup(rankings_request.text, "html.parser")
    rankings_last_updated = rankings_soup.find_all('p')[1].string[14:]

    # Convert String to Dates
    xml_site_map_date = time.strptime(xml_site_map_last_mod, "%Y-%m-%d")
    rankings_date = time.strptime(rankings_last_updated, "%Y-%m-%d")

    # Compare Dates
    most_recent_date = xml_site_map_last_mod
    if rankings_date > xml_site_map_date:
        most_recent_date = rankings_last_updated

    logging.info('The Website was Last Updated On: %s.', most_recent_date)
    return most_recent_date


def get_saved_images(images_json):
    try:
        with open(images_json, 'r') as read_file:
            images_names = json.load(read_file)
            return images_names
    except Exception as e:
        logging.error("Unable to get the filepath and name of images saved. Error Message: %s", str(e))
        print("Error: Could not get image names. Check logs.")
        exit()


# For every make and model
# 1. Get car image urls
# 2. save image
# 3. write the filepath of image to json
def save_images(directory, write_json):
    print("Retrieving Images...")
    makes_to_models = cars.get_makes_to_models()
    saved_filepaths = list()
    for make, models in makes_to_models.items():
        if make == 'Toyota':
            print("yo")
        print('\t', make)
        for model in models:
            if('overall' in directory):
                # Replace with url of overall car image
                image_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png?v=4'
                if(make == 'ISUZU'):
                    image_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png'
            else:
                # Get car generation image url
                image_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIRGeneration.png?v=4'
                if(make == 'ISUZU'):
                   break

            # Intended filepath of car image
            filepath = f'{directory}\{make}_{model}.png'
            # save images based on url and filepath
            image_saved = download_image(image_url, filepath)
            if(image_saved == True):
                saved_filepaths.append(filepath)

    # Write the file with passed in name
    with open(write_json, 'w') as write_file:
            json.dump(saved_filepaths, write_file)
    
    return saved_filepaths


def create_folder(filepath):
    # create folder if it does not exist
    folder = filepath.split('\\')[0]
    if not os.path.isdir(folder):
        os.makedirs(folder)


def download_image(url, filepath):
    try:
        create_folder(filepath)

        # Don't download image if it already exists
        if(os.path.exists(filepath)):
            return False
        else:
            downloaded_file = requests.get(url)
            open(filepath, 'wb').write(downloaded_file.content)
            logging.info("Saving filename: %s", filepath)
            return True
    except Exception as e:
        logging.error('Failed: %s. Could not save image: %s.', str(e), filepath)
        return False