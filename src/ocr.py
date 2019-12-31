# Standard library imports
import logging
import os

# Third party imports
import cv2
import pytesseract

# Local application imports
import cars


def convert_image_to_text(overall_image):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'    
    try:
        image_path = os.getcwd() + '\\' + overall_image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error("Unable to convert image to text Exception: %s", str(e))
        return str()


def filter_reliability_score_description(car_text):    
    description = str()
    reliability_score = float()

    # Convert strings to list. Then remove blank strings and spaces from list.
    lines = car_text.splitlines()
    lines = list(filter(lambda word: word != '', lines))
    lines = list(filter(lambda word: word != ' ', lines))

    for line in lines:
        # Car Description
        if line in cars.get_descriptors():
            description = line
        # Reliability Score
        elif "Score" in line:
            score = line.split(": ")[1].replace('-','.')
            if(score in "None"):
                reliability_score = -1.0
            else:
                reliability_score = float(score)
                if(reliability_score > 100):
                    reliability_score = reliability_score / 10

    logging.info("\t Score: %s | Car Description: %s", reliability_score, description)
    return reliability_score, description