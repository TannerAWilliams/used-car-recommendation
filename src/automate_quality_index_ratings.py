'''
The Quality Index Rating (QIR)

Offers an overall score based on the frequency of powertrain issues,
the mileage distribution of when those issues take place,
and the car age at the time of trade-in.

You can think of it as a weighted average where we look at a number of factors for a given car model,
and then get a single value indicating it’s overall long-term reliability.
'''

# Standard library imports
import logging

# Local application imports
import database
import scraping

if __name__ == "__main__":
    print("Running...")
    logging.basicConfig(filename="logs/appplication.log", filemode='w', level=logging.INFO)

    should_scrape_images = scraping.should_download_images()
    if(should_scrape_images):
        name_of_overall_images = scraping.save_images('images/overall', 'resources/saved_overall_images.json')
        name_of_generation_images = scraping.save_images('images/generation', 'resources/saved_generation_images.json')
    else:
        name_of_overall_images = scraping.get_saved_images('resources/saved_overall_images.json')
        name_of_generation_images = scraping.get_saved_images('resources/saved_generation_images.json')

    # TODO: Manufacter reliability score
    database.insert_overall_data(name_of_overall_images) # TODO
    #convert_generation_images_to_text(name_of_generation_images) 

    print("*** Done ***")