# TODO
# 1. Get each Car Generation Relibility Score
    # a. Image to Text    
    # b. Format the Text Data
# 2. Get Car Manufacter Relibility Score
    # a. Image to Text    
    # b. Format the Text Data
# 3. Insert All Data into Sqlite Tables
#   a. Car Overall Table
#   b. Car Generations Table
#   c. Car Manufacters Table
#   d. Cars Table (Everything) 
#   e. Think about changing all data to upper case

# 4. Analysis of Cars
#   a. Multi-Criteria Decision Analysis

# 5. Graph Cars

# 6. Implement APIs
#   a. edmunds.com
#   b. cars.com
#   c. cargurus.com

# 7. Store Used Car Listing on Database

# 8. Use Multicriteria Optimization to Decide what Cars to Buy

# 9. Django
'''
The Quality Index Rating (QIR)

Offers an overall score based on the frequency of powertrain issues,
the mileage distribution of when those issues take place,
and the car age at the time of trade-in.

You can think of it as a weighted average where we look at a number of factors for a given car model,
and then get a single value indicating it’s overall long-term reliability.
'''

from bs4 import BeautifulSoup
from PIL import Image
from pathlib import Path
import requests
import urllib.request
import shutil, os
import logging
import pytesseract
import time #converting strings to dates
import sqlite3
import json
import re
import cv2

def delete_all_files():
    # delete car folders
    shutil.rmtree("CarGenerationsImages", ignore_errors=True)
    shutil.rmtree("OverallCarImages", ignore_errors=True)
    # delete pickle files
    top = os.getcwd()
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            if(name.endswith(".json")):
                os.remove(os.path.join(root, name))
                logging.info('Deleted %s', name)
    
def should_scrape_images():
    try:
        with open('last_modified_date.json', 'r') as read_file:
            last_updated_date = json.load(read_file)
        
        last_modified_date = get_last_modified_date()
        if last_modified_date != last_updated_date:
            delete_all_files()
            write_file = open('last_modified_date.json', 'w')
            json.dump(last_modified_date, write_file)
            write_file.close()
            return True
        else:
            return False
    except FileNotFoundError:
        last_modified_date = get_last_modified_date()
        with open('last_modified_date.json', 'w') as write_file:
            json.dump(last_modified_date, write_file)
            return True
    except Exception as e:
        logging.error(
            "Unable to determine last date website was updated. Error Message: %s", str(e))
        return False


# Get the date the website was last modified
def get_last_modified_date():
    # Get Date from Site Map Index XML
    xml_site_map_request = requests.get(
        'http://www.dashboard-light.com/sitemap_index.xml')
    xml_site_map_soup = BeautifulSoup(xml_site_map_request.text, "html.parser")
    # .string[:-15]
    xml_site_map_last_mod = xml_site_map_soup.lastmod.string[:10]
    # Get Date from the Rankings Page
    rankings_request = requests.get('http://dashboard-light.com/rankings.html')
    rankings_soup = BeautifulSoup(rankings_request.text, "html.parser")
    rankings_last_updated = rankings_soup.find_all(
        'p')[1].string[-10:]  # .string[14:]

    # Convert String to Dates
    xml_site_map_date = time.strptime(xml_site_map_last_mod, "%Y-%m-%d")
    rankings_date = time.strptime(rankings_last_updated, "%Y-%m-%d")

    # Compare Dates
    most_recent_date = xml_site_map_last_mod
    if rankings_date > xml_site_map_date:
        most_recent_date = rankings_last_updated

    logging.info('The Website was Last Updated On: %s.', most_recent_date)
    return most_recent_date


def get_saved_car_images(images_json):
    try:
        with open(images_json, 'r') as read_file:
            images_names = json.load(read_file)
            return images_names
    except Exception as e:
        logging.error(
            "Unable to get the filepath and name of images saved. Error Message: %s", str(e))
        print("Error: Could not get image names. Check logs.")
        exit()


def save_image(url, filename):
    # create folder if it does not exist
    folder = filename.split('\\')[0]
    if not os.path.isdir(folder):
        os.makedirs(folder)
    
    try:
        urllib.request.urlretrieve(url, filename)
        logging.info("Saving filename: %s", filename)
        return True
    except Exception as e:
        logging.error('Failed: %s. Could not save image: %s.', str(e), filename)
        return False


def save_car_images(directory, file_name):
    makes_to_models = get_makes_to_models()

    print("Retrieving Images...")
    saved_cars = list()
    for make, models in makes_to_models.items():
        print('\t', make)
        for model in models:
            # Get url of car image
            car_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIRGeneration.png?v=4'
            if('Overall' in directory):
                # Replace with url of overall car image
                car_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png?v=4'
            if(make == 'ISUZU'):
                car_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png'
                
            # Get name of file and path
            car_filename = f'{directory}\{make}_{model}.png'

            # save images based on url and filename
            car_image_saved = save_image(car_png_url, car_filename)
            if(car_image_saved == True):
                saved_cars.append(car_filename)

    # Save the file name 
    with open(file_name, 'w') as write_file:
            json.dump(saved_cars, write_file)
    return saved_cars


# This section gets every model for each make
def get_makes_to_models():
    print("Getting Models...")
    try:
        with open("makes_to_models.json", "r") as read_file:
            makes_to_models = json.load(read_file)
            logging.info(
                'Dictionary with Key=Make and Value=Models - %s.', makes_to_models)
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
                if company == 'Land_Rover':
                    models_in_make = [
                        'Defender', 'Discovery', 'Freelander', 'LR2', 'LR3', 'LR4', 'Range_Rover']

                # Go to section where the models are located
                for div in soup.findAll('div', class_='article'):
                    for links in div.find_all('a'):
                        text = links.contents[0]
                        # checks if text contains the company
                        is_a_model = text.find(company)
                        if(is_a_model == 0):
                            # format text
                            current_model = text[len(company)+1:]
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
        with open('makes_to_models.json', 'w') as write_file:
            json.dump(makes_to_models, write_file)
            return makes_to_models



# InsufficientData, Chronic Reliability Issues, Well Below Average, Below Average
# Average, Above Average, Well Above Average, Exceptional
def get_descriptors():
    return ['InsuffcientData', 'Chronic Reliability Issues', 'Well Below Average', 'Below Average', 'Average', 'Above Average', 'Well Above Average', 'Exceptional']


# Get all the makes in the website
def get_makes():
    print("Getting Makes...")
    try:
        with open("makes.json", "r") as read_file:
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
                    if(html_index != -1):
                        make = full_url[18:html_index]
                        logging.info("Scraped: Make: %s", make)
                        makes.append(make)
        except Exception as e:
            logging.error(
                "Unable to retrieve makes. Error Message: %s", str(e))

        with open("makes.json", "w") as write_file:
            json.dump(makes, write_file)
            return makes


# TODO. Look into this method I think it may not work.
# The method returns a dictionary with every car nd their corresponding category
def get_categories_to_subdirectories():
    try:
        with open('car_categories_to_subdirectories.json', 'r') as read_file:
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
                    if(index != -1):
                        subdirectory = attribute[18:index-6]
                        category = attribute[index+1:-4]
                        logging.info("Scraped - Category: %s", category)
                        car_categories_to_subdirectories[category] = subdirectory
        except Exception as e:
            logging.error(
                "Unable to retrieve car categories. Error Message: %s", str(e))

        with open('car.json', 'w') as write_file:
            json.dump(car_categories_to_subdirectories, write_file)
            return car_categories_to_subdirectories


# This section return a dictionary for each model and its corresponding car category
def get_cars_to_categories():
    try:
        with open('cars_to_categories.json', 'r') as read_file:
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
                    if(index != -1):
                        car = attribute[index+1:-4].upper()
                        logging.info("Scraped - Car: %s", car)
                        cars_to_categories[car] = category
            except Exception as e:
                logging.error(
                    "Unable to retrieve category for %s. Error Message: %s", car, str(e))
        with open("cars_to_categories.json", "w") as write_file:
            json.dump(cars_to_categories, write_file)
            return cars_to_categories


def get_category(car_name):
    try:
        with open('cars_to_categories.json', 'r') as read_file:
            cars_to_categories = json.load(read_file)
    except FileNotFoundError:
        cars_to_categories = get_cars_to_categories();
    
    return cars_to_categories[car_name]

def get_make_model_from_image(image_path):
    car_name = image_path.split('\\')[1][:-4].split('_')
    makes_to_models = get_makes_to_models()

    make = car_name[0]
    if makes_to_models.get(make):
        model = " ".join(car_name[1:])
    else:
        make = " ".join(car_name[:2])
        model = " ".join(car_name[2:])
    
    return make, model
    logging.info('%s %s', make, model)


def convert_overall_car_images_to_text(overall_image):
    print("Converting Overall Rating Images to Text")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'    
    try:
        image_path = os.getcwd() + '\\' + overall_image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(
            "Unable to convert image:%s to text; Exception: %s;", str(e))


def filter_description_reliability_score(car_text):
    overall_reliability_score = None
    overall_description = None
    
    # Convert strings to list. Then remove blank strings and spaces from list.
    lines = car_text.splitlines()
    lines = list(filter(lambda word: word != '', lines))
    lines = list(filter(lambda word: word != ' ', lines))

    for line in lines:
        # Car Description
        if line in get_descriptors():
            description = line
        # Reliability Score
        elif "Score" in line:
            score = line.split(": ")[1].replace('-','.')
            if(score in "None"):
                reliability_score = -1.0
            else:
                reliability_score = float(score)

    logging.info("\t Score: %s; Description: %s;", overall_reliability_score, overall_description)
    return reliability_score, description


def insert_overall_car_data(filenames_list):
    for overall_image in filenames_list:
        text = convert_overall_car_images_to_text(overall_image)
        reliability_score, description = filter_description_reliability_score(text)
        make, model = get_make_model_from_image(overall_image)
        #TODO. insert data
            #TODO. dictionary with key(string)= Honda Accord and value(oatoat)=82.4;  
            # make_model_to_overall_reliability_score.


# TODO
# Scans words from image
# Return a list of lists.
#   i.e. Each list with be each individual cars relevant information
def convert_car_generations_images_to_text(filenames_list):
    print("Converting Images to Text")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for image in filenames_list:
        try:
            image_path = os.getcwd() + '\\' + image
            img = cv2.imread(image_path)
            text = pytesseract.image_to_string(img)
            # formatted_data = get_formatted_data(text)
            # insert_data_to_table()
            logging.info("%s: %s", image_path, text)
        except Exception as e:
            logging.error(
                "Unable to convert image:%s to text. Exception: %s", image, str(e))

#def get_formatted_data(text):

#def insert_data_to_table():   

    # TODO. Insert a row per generation or per year
        # make TEXT, model TEXT, year INTEGER, category TEXT, reliability_score REAL, overview TEXT, car_rating_average REAL, manufacturer_quality_index_rating REAL
    # insert_car_data_into_database(reliability_scores, years, make, model, descriptions, car_category, car_average_reliability_score, manufacturer_rating)
    

if __name__ == "__main__":
    logging.basicConfig(filename="logs/appplication.log", filemode='w', level=logging.INFO)

    should_scrape_images = should_scrape_images()
    if(should_scrape_images):
        name_of_overall_car_images = save_car_images('OverallCarImages', 'saved_overall_car_images.json')
        name_of_car_generations_images = save_car_images('CarGenerationsImages', 'saved_car_generations_images.json')
    else:
        name_of_overall_car_images = get_saved_car_images('saved_overall_car_images.json')
        name_of_car_generations_images = get_saved_car_images('saved_car_generations_images.json')

    # TODO: Manufacter reliability score
    insert_overall_car_data(name_of_overall_car_images) # TODO
    convert_car_generations_images_to_text(name_of_car_generations_images) 
   




'''

# TODO - Database. import sqlite3
# Table Called - Cars
# Column
# Reliability Score
# Year
# Make
# Model Name
# Description
# Car Type
# Manufactor Score
#

# Table Called - summary
# Column
# Reliability Score
# Make
# Model
# Description

# Each Make of Cars Has a table
# Table Called - Cars By Make

# Each Category of Cars/Size has a table
# Table Called - Cars By Category
# Make + Model Name
# Reliability Score
# Descriptor
# i.e. Chronic Reliability Issues
# i.e. InsufficientData

# Manufacturer Quality Index
# Columns
# Make
# Score


# Incorporate Used Car Sites API
# Cars.com


# Multi-Criteria Decision Analysis
# Multi-Objective Optimization
# Vector Optimization
# Multicriteria Optimization
# Multiattribute optimization
# Pareto optimization
# Models
# Weighted Sum Model
# Weighted Product Model
# TOPSIS
# Pareto Frontier of Cars
# QIR of Car
# Year of Car
# Mileage of Car
# Price of Car

# pymoo. Last released: Apr 26, 2019
#
# PyGMO
# https://esa.github.io/pygmo/install.html
#
# scikit criteria
# skcriteria.madm import closeness, simple
# https://buildmedia.readthedocs.org/media/pdf/scikit-criteria/latest/scikit-criteria.pdf

'''




'''
** Future Methods **

def create_table():
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
  
    c.execute('CREATE TABLE IF NOT EXISTS cars(reliability_score REAL, year INTEGER, make TEXT, model TEXT, overview TEXT, category TEXT, manufactor_quality_index_rating REAL )')
    c.execute("INSERT INTO cars VALUES(0.0, 1996, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(0.0, 1997, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(0.0, 1998, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(0.0, 1999, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(17.9, 2001, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(17.9, 2002, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO cars VALUES(17.9, 2003, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    
    conn.commit()
    c.close()
    conn.close()

def is_pareto_efficient_dumb(costs):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
    """
    is_efficient = np.ones(costs.shape[0], dtype = bool)
    for i, c in enumerate(costs):
        is_efficient[i] = np.all(np.any(costs[:i]>c, axis=1)) and np.all(np.any(costs[i+1:]>c, axis=1))
    return is_efficient

#TODO
#Store values into database
#car name
def insert_car_data_into_database(reliability_scores, years, make, model, descriptions, car_category, car_average_reliability_score, manufactor_quality_index_rating):
    print("hey")
'''



