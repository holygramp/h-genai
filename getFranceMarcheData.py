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
from coreScrapingFunctions import fetch_html_selenium, setup_selenium
import time
from openai import OpenAI
from config import USER_AGENTS,HEADLESS_OPTIONS
import requests
import pandas as pd


def getAllAOs(nom_dep, path_to_csv='h-genai/departements-france.csv',  driver=None, attended_mode=False, i=1):
    """
    Retrieve all the AOs of the website given the name of the department.
    Output format:
        AO_titles=[string]
        AO_links[string]
    """
    df = pd.read_csv(path_to_csv)
    nb_dep = df.loc[df["nom_departement"] == nom_dep, "code_departement"].values[0]
    AO_links = []
    AO_titles = []
    if driver == None:
        driver = setup_selenium(False)
    page_html = fetch_html_selenium("https://www.francemarches.com/recherche?q=&departements%5B0%5D=21&ordre=date-publication-desc&page=1", attended_mode, driver)
    while "Votre recherche ne ramène aucun résultat" not in page_html:
        page_html = fetch_html_selenium("https://www.francemarches.com/recherche?q=&departements%5B0%5D="+str(nb_dep)+"&ordre=date-publication-desc&page="+str(i), attended_mode, driver)
        if "src=\"https://geo.captcha" in page_html:
            print('coucou')
            print("Captcha error, remplissez le et appuyez sur Espace")
            keyboard.wait("space")
            print("Reprise du scrapping")
            return getAllAOs(nb_dep,path_to_csv, driver, attended_mode, i)
        soup = BeautifulSoup(page_html, 'html.parser')
        AOs = soup.find_all("div", class_="offre__header-link")
        for ao in AOs:
            title = ao.get_text()
            link = ao.find_previous("a", class_="offre").get("href")
            AO_links.append(link)
            AO_titles.append(title)
            driver.quit()
            return AO_titles, AO_links
        i+=1
    driver.quit()
    return AO_titles, AO_links
      
# print(getAllAOs("Ain"))
