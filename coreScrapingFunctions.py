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

def setup_selenium(attended_mode=False):
    """
    Prepare a driver to scrape data with all the right options. Do not touch !
    """
    options = Options()
    service = Service(ChromeDriverManager().install())

    # Apply headless options based on whether the code is running in Docker
        # Not running inside Docker, use the normal headless options
    for option in HEADLESS_OPTIONS:
        options.add_argument(option)

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_html_selenium(url, attended_mode=False, driver=None):
    """
    Fetch data from a URL. Do not touch !
    """
    if driver is None:
        driver = setup_selenium(attended_mode)
        should_quit = True
        if not attended_mode:
            driver.get(url)
    else:
        should_quit = False
        # Do not navigate to the URL if in attended mode and driver is already initialized
        if not attended_mode:
            driver.get(url)

    try:
        if not attended_mode:
            # Add more realistic actions like scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.2);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1);")
            time.sleep(random.uniform(1.1, 1.8))
        # Get the page source from the current page
        html = driver.page_source
        return html
    finally:
        if should_quit:
            driver.quit()