from selenium import webdriver
import sys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
import random 
import re
import keyboard
import subprocess
from langchain.tools import DuckDuckGoSearchRun
import time
from openai import OpenAI
from config import USER_AGENTS,PRICING,HEADLESS_OPTIONS
import requests

def getInseeCode(ville):
    """
    Retrieves the INSEE code of a city given it's name.
    Output format: integer
    """
    response = requests.get("https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-communes/records?where=com_name%20like%20%20%22"+ville+"%22&limit=1")
    if response.status_code == 200:
        data = response.json()
        insee_code = data["results"][0]["insee"]
        epci_code = data["results"][0]["epci_code"]
        return(insee_code, epci_code)
    else:
        print("Erreur dans le nom de la ville ou ailleurs")
        return(None)
    
def getInseeData(ville):
    """
    Retrieves :
        - Nombre d'habitants
        - Densité
        - Superficie
        - Part des résidences principales
        - Part des résidences secondaires
        - Part des logements vacants
        - Taux de chômage des 15 à 64 ans
        - Part de l'agriculture, en %
        - Part de l'industrie, en %
        - Part de la construction, en %
        - Part du commerce, transports et services divers, en %
        - Part de l'administration publique, enseignement, santé et action sociale, en %
    given the city name.

    Output format: data_types: {'population': 'Population en 2021', 'densité': "Densité de la population (nombre d'habitants au km²) en 2021",
                    'superficie': 'Superficie en 2021, en km²', 'part-resid-princ': 'Part des résidences principales en 2021, en %',
                    'part-resid-second': 'Part des résidences secondaires (y compris les logements occasionnels) en 2021, en\n %',
                    'part-log-vac': 'Part des logements vacants en 2021, en %', 'chomage': 'Taux de chômage des 15 à 64 ans en 2021',
                    'agriculture': "Part de l'agriculture, en %", 'industrie': "Part de l'industrie, en %", 'construction': 'Part de la
                    construction, en %', 'commerce': 'Part du commerce, transports et services divers, en %', 'administration': "Part de
                    l'administration publique, enseignement, santé et action sociale, en %"}

                    combined_json: {'EPCI': {'population': '159 346', 'densité':
                    '3 943,2', 'superficie': '40,4', 'part-resid-princ': '88,9', 'part-resid-second': '3,7', 'part-log-vac': '7,4',
                    'chomage': '13,5', 'agriculture': '0,2', 'industrie': '4,1', 'construction': '5,7', 'commerce': '74,1',
                    'administration': '15,9'}, 
                    'CITY': {'population': '257 193', 'densité': '1 071,8', 'superficie': '240,0',
                    'part-resid-princ': '90,4', 'part-resid-second': '2,9', 'part-log-vac': '6,7', 'chomage': '12,6', 'agriculture': '0,7',
                    'industrie': '5,5', 'construction': '9,0', 'commerce': '70,9', 'administration': '13,9'}}
    """
    sys.stdout.reconfigure(encoding='utf-8')
    insee_code, epci_code = getInseeCode(ville)
    if insee_code == None:
        return None
    
    res = requests.get(f"https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-{epci_code}+COM-{insee_code}")
    soup = BeautifulSoup(res.content, 'html.parser', from_encoding='utf-8')
    # Find all tr elements
    tr_tags = soup.find_all('tr')

    # Initialize lists for results
    data_types = {}
    epci_numbers = {}
    city_numbers = {}

    # Iterate through tr elements
    for tr in tr_tags:
        # Look for the first th element within the current tr
        th = tr.find('th')
        
        # Check if th exists and its text starts with "Population en"
        if th and th.text.strip().startswith("Population en"):
            # Get the text from th
            
            data_types["population"] = th.text.strip()
            
            # Find td elements within the same tr
            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["population"] = td_tags[0].text.strip()
                city_numbers["population"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Densité"):
            data_types["densité"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["densité"] = td_tags[0].text.strip()
                city_numbers["densité"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Superficie"):
            data_types["superficie"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["superficie"] = td_tags[0].text.strip()
                city_numbers["superficie"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part des résidences principales"):
            data_types["part-resid-princ"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["part-resid-princ"] = td_tags[0].text.strip()
                city_numbers["part-resid-princ"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part des résidences secondaires"):
            data_types["part-resid-second"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["part-resid-second"] = td_tags[0].text.strip()
                city_numbers["part-resid-second"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part des logements vacants"):
            data_types["part-log-vac"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["part-log-vac"] = td_tags[0].text.strip()
                city_numbers["part-log-vac"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Taux de chômage des 15 à 64 ans "):
            data_types["chomage"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["chomage"] = td_tags[0].text.strip()
                city_numbers["chomage"] = td_tags[1].text.strip()


        elif th and th.text.strip().startswith("Part de l'agriculture, "):
            data_types["agriculture"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["agriculture"] = td_tags[0].text.strip()
                city_numbers["agriculture"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part de l'industrie, "):
            data_types["industrie"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["industrie"] = td_tags[0].text.strip()
                city_numbers["industrie"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part de la construction, "):
            data_types["construction"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["construction"] = td_tags[0].text.strip()
                city_numbers["construction"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part du commerce, transports "):
            data_types["commerce"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["commerce"] = td_tags[0].text.strip()
                city_numbers["commerce"] = td_tags[1].text.strip()

        elif th and th.text.strip().startswith("Part de l'administration publique, "):
            data_types["administration"] = th.text.strip()

            td_tags = tr.find_all('td', limit=2)
            
            # If we found 2 td elements, add their values to our lists
            if len(td_tags) == 2:
                epci_numbers["administration"] = td_tags[0].text.strip()
                city_numbers["administration"] = td_tags[1].text.strip()
    
    for key in epci_numbers.keys():
        epci_numbers[key] = epci_numbers[key] .replace("\xa0", " ")
    for key in city_numbers.keys():
        city_numbers[key] = city_numbers[key] .replace("\xa0", " ")
    
    combined_json = {
        "EPCI": city_numbers,
        "CITY": epci_numbers
    }
    return(data_types, combined_json)

# print(getInseeData("Dijon"))