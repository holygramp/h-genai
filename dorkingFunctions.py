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
from config import USER_AGENTS,HEADLESS_OPTIONS
import requests
from coreScrapingFunctions import setup_selenium, fetch_html_selenium
import pandas as pd


def getAllBudgetsPrimitifs(path_to_csv="h-genai/villes_sites.csv"):
    """
    Retrieves the Budgets Primitifs from all the cities listed in the input csv.
    Output format: 
        [https://cdn.paris.fr/paris/2024/02/20/1-bp-2024-rapport-budget-vote-WxDD.pdf
        https://www.marseille.fr/sites/default/files/contenu/mairie/Budget/pdf/rapport_de_presentation_budget_primitif_2024-c.pdf
        https://www.lyon.fr/sites/lyonfr/files/content/documents/2024-06/synthese_sur_le_budget_primitif_2024_0.pdf
        https://metropole.toulouse.fr/sites/toulouse-fr/files/2022-09/rapport_bp2021.pdf
        https://www.nice.fr/uploads/media/default/0001/33/Budget-2024-Pr%C3%A9sentation-br%C3%A8ve-et-synth%C3%A9tique-du-budget-primitif.pdf
        https://cdn.paris.fr/paris/2024/02/20/1-bp-2024-rapport-budget-vote-WxDD.pdf]
    """
    df = pd.read_csv(path_to_csv)
    PDFs = []
    # Itérer sur chaque ligne du DataFrame pour effectuer une recherche
    for _, row in df.iterrows():
        ville = row['Ville']
        site = row['Site Internet']
        query = f'https://www.google.com/search?q=("budget primitif" OR "Budget Primitif" OR "BUDGET PRIMITIF") inurl:{ville} filetype:pdf'
        query_second_chance = f'https://www.google.com/search?q=("budget primitif" OR "Budget Primitif" OR "BUDGET PRIMITIF") site:{site} filetype:pdf'
        PDFs.append(getFirstURL(query, query_second_chance))
    return PDFs

def getAllDOB(path_to_csv="h-genai/villes_sites.csv"):
    """
    Retrieves the Débats d'orientation budgétaire from all the cities listed in the input csv.
    Output format: 
        [https://www.belfort.fr/fileadmin/documents/Mairie/budget/2023/ANNEXE_ROB_2024.pdf,
        https://www.dijon-metropole.fr/wp-content/uploads/sites/25/2024/12/DEL_2024_31_DOB-2025.pdf
       ]
    """
    df = pd.read_csv(path_to_csv)
    PDFs = []
    # Itérer sur chaque ligne du DataFrame pour effectuer une recherche
    for _, row in df.iterrows():
        ville = row['Ville']
        query = f'https://www.google.com/search?q="débat d\'orientation budgétaire" after:2024-01-01 inurl:{ville} filetype:pdf'
        query_second_chance = f'https://www.google.com/search?q="débat d\'orientation budgétaire" after:2023-01-01 inurl:{ville} filetype:pdf'
        PDFs.append(getFirstURL(query, query_second_chance, False, None, 1))
    return PDFs

def getFirstURL(query, query2, attended_mode=False, driver=None, n_tries=0):
    """
    Retrieves the first URL in a google page after a google dork query.
    If there is no result with the first query, we try the second one.
    The function handles Captchas.

    Output format:
        string (URL)
    """
    if driver == None:
        driver = setup_selenium(False)
    res = fetch_html_selenium(query,attended_mode, driver)
    if "propos de cette page" in res:
        print("Captcha error, remplissez le et appuyez sur Espace")
        keyboard.wait("space")
        print("Reprise du scrapping")
        return getFirstURL(query, attended_mode, driver, n_tries)
    elif "Aucun résultat" in res and n_tries < 1:
        return getFirstURL(query2, attended_mode, driver, n_tries+1)
    elif "Aucun résultat" in res and n_tries >= 1:
        print("Pas de BP trouvé après 2 tentatives")
        driver.quit()
        return None
    soup = BeautifulSoup(res, 'html.parser')
    a_tags = soup.find_all("a", jsname="UWckNb")
    for a_tag in a_tags:
        if a_tag.has_attr('href') and a_tag.get("href") is not None:
            href = a_tag.get("href")
            if href and href.endswith(".pdf"):
                driver.quit()
                return(a_tag.get("href"))


# print(getAllBudgetsPrimitifs()[0])
# print(getAllDOB())
