# Standard library imports
import logging
import sqlite3

# Local application imports
import database
import cars
import ocr

def create_overall_table(filenames_list):
    # if table does not exist
        # create table
    return None

def insert_overall_data(filenames_list):
    get_overall_data(filenames_list)
    return None

# TODO
def get_overall_data(filenames_list):
     for overall_image in filenames_list:
        text = ocr.convert_image_to_text(overall_image)
        make, model = cars.get_make_model_from_image(overall_image)
        reliability_score, description = ocr.filter_reliability_score_description(text)


def create_generation_table():
    return None
    # make TEXT, model TEXT, year INTEGER, category TEXT, reliability_score REAL, overview TEXT, car_rating_average REAL, manufacturer_quality_index_rating REAL


def get_generation_data(filenames_list):
    return None
    # for generation_image in filenames_list:
    #     text = utility.convert_image_to_text(overall_image)
    #     make, model = car_data.get_make_model_from_image(overall_image)
        # TODO. filter relevant information.
        # TODO. dictionary with key(string)= Honda Accord and value(oatoat)=82.4 
        # TODO. make_model_to_overall_reliability_score.


# TODO
def insert_generation_data(filenames_list):
    return None
    # TODO. Insert a row per generation or per year
        # reliability_scores, years, make, model, descriptions, car_category, car_average_reliability_score, manufacturer_rating):

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