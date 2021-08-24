# Standard library imports
import logging
import json
import re

# Third party imports
from bs4 import BeautifulSoup
import requests


# Get all the makes in the website
def get_makes():
    print("Getting Makes...")
    try:
        with open("resources/makes.json", "r") as read_file:
            makes = json.load(read_file)
            logging.info('List of Makes - %s.', makes)
            return makes
    except FileNotFoundError:
        makes = list()
        url = 'http://www.dashboard-light.com/'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            for div in soup.find_all('div', class_='vehicle-makes'):
                for links in div.find_all('a'):
                    full_url = str(links)
                    html_index = full_url.find(".html")
                    if (html_index != -1):
                        make = full_url[18:html_index]
                        logging.info("Scraped: Make: %s", make)
                        makes.append(make)
        except Exception as e:
            logging.error(
                "Unable to retrieve makes. Error Message: %s", str(e))

        with open("resources/makes.json", "w") as write_file:
            json.dump(makes, write_file)
            return makes


# This section gets every model for each make
def get_makes_to_models():
    try:
        with open("resources/makes_to_models.json", "r") as read_file:
            makes_to_models = json.load(read_file)
            return makes_to_models
    except FileNotFoundError:
        # list of all the makes
        makes = get_makes()
        makes_to_models = dict()
        # go through each make and parse their specific web page
        for company in makes:
            models_in_make = list()
            url = f'http://www.dashboard-light.com/reports/{company}.html'
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            try:
                if company == 'ISUZU':
                    models_in_make = ['Amigo', 'Ascender', 'Axiom', 'Axiom', 'Hombre', 'i_Series',
                                      'Npr', 'Oasis', 'Pickup', 'Rodeo', 'Spacecab', 'Trooper', 'VehiCROSS']
                elif company == 'Land_Rover':
                    models_in_make = [
                        'Defender', 'Discovery', 'Freelander', 'LR2', 'LR3', 'LR4', 'Range_Rover']

                # Go to section where the models are located
                for div in soup.findAll('div', class_='article'):
                    for links in div.find_all('a'):
                        text = links.contents[0]
                        # checks if text contains the company
                        is_a_model = text.find(company)
                        if (is_a_model == 0):
                            # format text
                            current_model = text[len(company) + 1:]
                            current_model = current_model.replace(' ', '_')
                            current_model = current_model.replace('/', '_')
                            logging.info('Scraped - Make: %s. Model: %s.',
                                         company, current_model)
                            models_in_make.append(current_model)
                logging.info('Make - %s. Models - %s.',
                             company, models_in_make)
                makes_to_models[company] = models_in_make
            except Exception as e:
                logging.error(
                    "Unable to get Models. Error Message: %s", str(e))
        with open('resources/makes_to_models.json', 'w') as write_file:
            json.dump(makes_to_models, write_file)
            return makes_to_models


def get_category(car_name):
    try:
        with open('resources/cars_to_categories.json', 'r') as read_file:
            cars_to_categories = json.load(read_file)
    except FileNotFoundError:
        cars_to_categories = get_cars_to_categories()

    return cars_to_categories[car_name]


# TODO. Look into this method I think it may not work.
# The method returns a dictionary with every car nd their corresponding category
def get_categories_to_subdirectories():
    try:
        with open('resources/categories_to_subdirectories.json', 'r') as read_file:
            car_categories_to_subdirectories = json.load(read_file)
            logging.info('List of Car Categories - %s.',
                         car_categories_to_subdirectories)
            return car_categories_to_subdirectories
    except FileNotFoundError:
        car_categories_to_subdirectories = dict()
        url = 'http://www.dashboard-light.com/'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            for div in soup.find_all('div', class_='vehicle-categories'):
                for hyperlinks in div.find_all('a'):
                    attribute = str(hyperlinks)
                    index = attribute.find(">")
                    if (index != -1):
                        subdirectory = attribute[18:index - 6]
                        category = attribute[index + 1:-4]
                        logging.info("Scraped - Category: %s", category)
                        car_categories_to_subdirectories[category] = subdirectory
        except Exception as e:
            logging.error(
                "Unable to retrieve car categories. Error Message: %s", str(e))

        with open('resources/categories_to_subdirectories.json', 'w') as write_file:
            json.dump(car_categories_to_subdirectories, write_file)
            return car_categories_to_subdirectories


# This section return a dictionary for each model and its corresponding car category
def get_cars_to_categories():
    try:
        with open('resources/cars_to_categories.json', 'r') as read_file:
            cars_to_categories = json.load(read_file)
            logging.info(
                'Dictionary of Cars to Categories: %s.', cars_to_categories)
            return cars_to_categories
    except FileNotFoundError:
        # list of all the makes
        categories_to_subdirectories = get_categories_to_subdirectories()
        cars_to_categories = dict()
        # go through each make and parse their specific web page
        for category, subdirectory in categories_to_subdirectories.items():
            url = f'http://www.dashboard-light.com/reports/{subdirectory}.html'
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
                for a in soup.find_all(href=re.compile("vehicles")):
                    attribute = str(a)
                    index = attribute.find('>')
                    if (index != -1):
                        car = attribute[index + 1:-4].upper()
                        logging.info("Scraped - Car: %s", car)
                        cars_to_categories[car] = category
            except Exception as e:
                logging.error(
                    "Unable to retrieve category for %s. Error Message: %s", car, str(e))
        with open("resources/cars_to_categories.json", "w") as write_file:
            json.dump(cars_to_categories, write_file)
            return cars_to_categories


# InsufficientData, Chronic Reliability Issues, Well Below Average, Below Average
# Average, Above Average, Well Above Average, Exceptional
def get_descriptors():
    return ['InsufficientData', 'Chronic Reliability Issues', 'Well Below Average', 'Below Average', 'Average',
            'Above Average', 'Well Above Average', 'Exceptional']


def get_make_model_from_image(image_path):
    car_name = image_path.split('\\')[1][:-4].split('_')
    makes_to_models = get_makes_to_models()

    make = car_name[0]
    if makes_to_models.get(make):
        model = " ".join(car_name[1:])
    else:
        make = " ".join(car_name[:2])
        model = " ".join(car_name[2:])

    logging.info('%s %s', make, model)
    return make, model
