# TODO
# 1. Get/Retrieve/e Average Relibility Score of Vehicle
# 2. Get Manufacter Relibility Score
# 3. Image to Text    
    # a. Format the Text Data
# 4. Insert Data into Sqlite

# 5. Analysis of Cars
# Multi-Criteria Decision Analysis

# 6. Graph Cars

# 7. Implement APIs
#   a. edmunds.com
#   b. cars.com
#   c. cargurus.com
# 8. Store Used Car Listing on Database
# 9. Use Multicriteria Optimization to Decide what Cars to Buy

'''
The Quality Index Rating (QIR)

Offers an overall score based on the frequency of powertrain issues,
the mileage distribution of when those issues take place,
and the vehicle age at the time of trade-in.

You can think of it as a weighted average where we look at a number of factors for a given vehicle model,
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
import time
import sqlite3
import pickle
import json
import re
# import colorama

def delete_all_files():
    # delete vehicle folder
    shutil.rmtree("Vehicles", ignore_errors=True)
    shutil.rmtree("AverageCar", ignore_errors=True)
    # delete pickle files
    top = os.getcwd()
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            if(name.endswith(".pickle")):
                os.remove(os.path.join(root, name))
                logging.debug('Deleted %s', name)
    
def should_update_images():
    try:
        with open('last_modified_date.pickle', 'r') as pickle_in:
            last_updated_date = pickle.load(pickle_in)
        last_modified_date = get_last_modified_date()
        if last_modified_date != last_updated_date:
            delete_all_files()
            pickle_out = open('last_modified_date.pickle', 'w')
            pickle.dump(last_modified_date, pickle_out)
            pickle_out.close()
            return True
        else:
            return False
    except FileNotFoundError:
        last_modified_date = get_last_modified_date()
        with open('last_modified_date.pickle', 'w') as pickle_out:
            pickle.dump(last_modified_date, pickle_out)
            return True
    except Exception as e:
        logging.error(
            "Unable to determine last date website was updated. Error Message: %s", str(e))
        return False


# TODO - Get more websites
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


def save_new_images():
    # Ask your if they want separate folder for each manufactuer
    #should_create_separate_folders = ask_for_user_response()
    create_folders = False
    # saved images by getting makes, models, and associated images of vehicles
    saved_average_images, saved_vehicle_images   = save_quality_index_rating_images(create_folders)
    with open('saved_images_names.pickle', 'w') as pickle_out:
        pickle.dump(saved_average_images, pickle_out)
        pickle.dump(saved_vehicle_images, pickle_out)
        return saved_average_images, saved_vehicle_images


def ask_for_user_response():
    response = str(input(
        "Would you like to save the vehicle quality index rating images into separate folders by make? [Y / n]: ")).lower()
    create_folders = False
    if response in ("t", "true", "y", "yes"):
        create_folders = True
    
    return create_folders


def get_saved_images_names():
    try:
        with open('saved_images_names.pickle', 'r') as pickle_in:
            images_names = pickle.load(pickle_in)
            images_names2 = pickle.load(pickle_in)
            return images_names, images_names2
    except Exception as e:
        logging.error(
            "Unable to get the filepath and name of images saved. Error Message: %s", str(e))
        return None


def create_folders(directories):
    for folder in directories:
        if not os.path.exists(f'{folder}'):
            path = f'{folder}'
            os.mkdir(path)


def save_image(url, filename):
    #Always overwrite.
    try:
        urllib.request.urlretrieve(url, filename)
        logging.debug("Filename: %s", filename)
        return True
    except Exception as e:
        logging.error('Failed: %s \tCould not save_image.', str(e))
        return False


# Save Image
def save_quality_index_rating_images(have_folders):
    makes_models = get_makes_to_models()

    # Create folders
    directories = ['AverageCar', 'Vehicles']
    create_folders(directories)

    print("Retrieving Images...")
    saved_averages = list()
    saved_vehicles = list()
    for make, models in makes_models.items():
        print('\t', make)
        for model in models:
            # Get url of photos
            average_car_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIRGeneration.png?v=4'
            car_generations_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png?v=4'
            if(make == "ISUZU"):
                average_car_png_url = f'http://www.dashboard-light.com/vehicles/Resources/Images/{make}/{model}/QIR.png'
                car_generations_png_url = average_car_png_url

            # Get name of file and path
            average_car_filename = f'{directories[0]}\{make}_{model}.png'
            vehicle_filename = f'{directories[1]}\{make}_{model}.png'

            # save images based on url and filename
            average_car_image_saved = save_image(average_car_png_url, vehicle_filename)
            vehicle_image_saved = save_image(car_generations_png_url, average_car_filename)
            
            if(average_car_image_saved == True):
               saved_averages.append(average_car_image_saved)
            if(vehicle_image_saved == True):
                saved_vehicles.append(vehicle_filename)
    return saved_averages, saved_vehicles


# InsufficientData, Chronic Reliability Issues, Well Below Average, Below Average
# Average, Above Average, Well Above Average, Exceptional
def get_descriptors():
    return ['InsuffcientData', 'Chronic Reliability Issues', 'Well Below Average', 'Below Average', 'Average', 'Above Average', 'Well Above Average', 'Exceptional']


# Get all the makes in the website
def get_makes():
    print("Getting Makes...")
    try:
        with open("makes.pickle", "r") as pickle_in:
            makes = pickle.load(pickle_in)
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
                        logging.debug("Make: %s", make)
                        makes.append(make)
        except Exception as e:
            logging.error(
                "Unable to retrieve makes. Error Message: %s", str(e))

        with open("makes.pickle", "w") as pickle_out:
            pickle.dump(makes, pickle_out)
            return makes


# This section gets every model for each make
def get_makes_to_models():
    print("Getting Models...")
    try:
        with open("makes_to_models.pickle", "r") as pickle_in:
            makes_to_models = pickle.load(pickle_in)
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
                # TODO: Fix the hard coding of ISUZU & Land Rover
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
                            logging.debug('Make: %s. Model: %s.',
                                          company, current_model)
                            models_in_make.append(current_model)
                logging.info('Make - %s. Models - %s.',
                             company, models_in_make)
                makes_to_models[company] = models_in_make
            except Exception as e:
                logging.error(
                    "Unable to get Models. Error Message: %s", str(e))
        with open('makes_to_models.pickle', 'w') as pickle_out:
            pickle.dump(makes_to_models, pickle_out)
            return makes_to_models


# The method returns a dictionary with every car nd their corresponding category
def get_categories_to_subdirectories():
    try:
        with open('vehicle_categories_to_subdirectories.pickle', 'r') as pickle_in:
            vehicle_categories_to_subdirectories = pickle.load(pickle_in)
            logging.info('List of Vehicle Categories - %s.',
                         vehicle_categories_to_subdirectories)
            return vehicle_categories_to_subdirectories
    except FileNotFoundError:
        vehicle_categories_to_subdirectories = dict()
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
                        logging.debug("Category: %s", category)
                        vehicle_categories_to_subdirectories[category] = subdirectory
        except Exception as e:
            logging.error(
                "Unable to retrieve vehicle categories. Error Message: %s", str(e))

        with open('vehicle_categories_to_subdirectories.pickle', 'w') as pickle_out:
            pickle.dump(vehicle_categories_to_subdirectories, pickle_out)
            return vehicle_categories_to_subdirectories


# This section return a dictionary for each model and its corresponding vehicle category
def get_vehicles_to_categories():
    try:
        with open('vehicles_to_categories.pickle', 'r') as pickle_in:
            vehicles_to_categories = pickle.load(pickle_in)
            logging.info(
                'Dictionary of Vehicle to Categories - %s.', vehicles_to_categories)
            return vehicles_to_categories
    except FileNotFoundError:
        # list of all the makes
        categories_to_subdirectories = get_categories_to_subdirectories()
        vehicles_to_categories = dict()
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
                        vehicle = attribute[index+1:-4].upper()
                        logging.debug("Vehicle: %s", vehicle)
                        vehicles_to_categories[vehicle] = category
            except Exception as e:
                logging.error(
                    "Unable to retrieve category for %s. Error Message: %s", vehicle, str(e))
        with open("vehicles_to_categories.pickle", "w") as pickle_out:
            pickle.dump(vehicles_to_categories, pickle_out)
            return vehicles_to_categories

def get_category(vehicle_name):
    try:
        with open('vehicles_to_categories.pickle', 'r') as pickle_in:
            vehicles_to_categories = pickle.load(pickle_in)
    except FileNotFoundError:
        vehicles_to_categories = get_vehicles_to_categories();
    
    return vehicles_to_categories[vehicle_name]


def set_vehicle_to_average_rating(filenames_list):
    print("Converting Images to Text")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for average_image in filenames_list:
        try:
            image_path = os.getcwd() + '\\' + average_image
            text = pytesseract.image_to_string(Image.open(image_path))
            
            formatted_data = get_formatted_data(text)
            logging.info("%s: %s", image_path, text)
        except Exception as e:
            logging.error(
                "Unable to convert photo:%s to text. Exception: %s", str(e))

##TODO
def extract_text(average_vehicle_text):
    make = str()
    model = str()
    make_model = str()
    vehicle_average_reliability_score = 0
    
    #TODO
    # vehicle_rating_average
    # manufacturer_quality_index_rating (DICTIONARY: KEY make, VALUE score) 

    # Convert strings to list. Then remove blank strings and spaces from list.
    lines = average_vehicle_text.splitlines()
    lines = list(filter(lambda word: word != '', lines))
    lines = list(filter(lambda word: word != ' ', lines))

    # Go through each line of vehicle text and extract relevant data
    vehicle_name = lines[0]
    make = vehicle_name.split()[0]
    model = vehicle_name.split()[1]

# TODO
# Scans words from image
# Return a list of lists.
#   i.e. Each list with be each individual vehicles relevant information
def ocr_core(filenames_list):
    print("Converting Images to Text")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for image in filenames_list:
        try:
            image_path = os.getcwd() + '\\' + image
            text = pytesseract.image_to_string(Image.open(image_path))
            formatted_data = get_formatted_data(text)
            logging.info("%s: %s", image_path, text)
        except Exception as e:
            logging.error(
                "Unable to convert photo:%s to text. Exception: %s", image, str(e))



# TODO - Create a fuction that text the pytesseract text and format is to a list
def get_formatted_data(vehicle_text):
    years = list()
    reliability_scores = list()
    descriptions = list()
    make = str()
    model = str()
    vehicle_category = str()
    vehicle_average_reliability_score = str()
    manufacturer_rating = str()
    
    #TODO
    # vehicle_rating_average
    # manufacturer_quality_index_rating (DICTIONARY: KEY make, VALUE score) 

    # Convert strings to list. Then remove blank strings and spaces from list.
    lines = vehicle_text.splitlines()
    lines = list(filter(lambda word: word != '', lines))
    lines = list(filter(lambda word: word != ' ', lines))

    # Go through each line of vehicle text and extract relevant data
    vehicle_name = lines[0]
    make = vehicle_name.split()[0]
    model = vehicle_name.split()[1]
    vehicle_category = get_category(vehicle_name.upper()) #IMPROVEMENT: Make categories, make model, global variables. Look about namespaces in python
    #TODO
    # vehicle_rating_average REAL
    # manufacturer_quality_index_rating REAL

    # TODO determine which info I want to add to database
    for line in lines:
        # Vehicle Description
        if line in get_descriptors():
            descriptions.append(line)
        # Years
        if '-' in line:
            generation = line[:9]
            years.append(generation)
        # Reliability Score
        if 'Score' in line:
            score = line[19:]
            reliability_scores.append(score)
    print(vehicle_name)

    # TODO. Insert a row per generation or per year
     # make TEXT, model TEXT, year INTEGER, category TEXT, reliability_score REAL, overview TEXT, vehicle_rating_average REAL, manufacturer_quality_index_rating REAL
    # insert_car_data_into_database(reliability_scores, years, make, model, descriptions, vehicle_category, vehicle_average_reliability_score, manufacturer_rating)
   
    
    # Todo make sure this works by inserting data into text file
    # then store values into database


if __name__ == "__main__":
    logging.basicConfig(filename="app.log", filemode='w', level=logging.DEBUG)

    should_update = should_update_images()
    if(should_update):
        name_of_average_images, name_of_vehicle_images = save_new_images()
    else:
        name_of_average_images, name_of_vehicle_images = get_saved_images_names()

    set_vehicle_to_average_rating(name_of_average_images)
    ocr_core( name_of_vehicle_images)

    input('* Finished Press Enter to Close Program *')




'''

# TODO - Database. import sqlite3
# Table Called - Cars
# Column
# Reliability Score
# Year
# Make
# Model Name
# Description
# Vehicle Type
# Manufactor Score
#

# Table Called - summary
# Column
# Reliability Score
# Make
# Model
# Description

# Each Make of Cars Has a table
# Table Called - Vehicles By Make

# Each Category of vehicles/Size has a table
# Table Called - Vehicles By Category
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
# QIR of Vehicle
# Year of Vehicle
# Mileage of Vehicle
# Price of Vehicle

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
  
    c.execute('CREATE TABLE IF NOT EXISTS vehicles(reliability_score REAL, year INTEGER, make TEXT, model TEXT, overview TEXT, category TEXT, manufactor_quality_index_rating REAL )')
    c.execute("INSERT INTO vehicles VALUES(0.0, 1996, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(0.0, 1997, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(0.0, 1998, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(0.0, 1999, 'Acura', 'CL', 'Chronic Reliability Issues', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(17.9, 2001, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(17.9, 2002, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    c.execute("INSERT INTO vehicles VALUES(17.9, 2003, 'Acura', 'CL', 'Well Below Average', 'Mid-size Luxury', 41)")
    
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
def insert_car_data_into_database(reliability_scores, years, make, model, descriptions, vehicle_category, vehicle_average_reliability_score, manufactor_quality_index_rating):
    print("hey")
'''



