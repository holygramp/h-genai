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
from coreScrapingFunctions import setup_selenium, fetch_html_selenium


class Experience(BaseModel):
    job: str
    duration: str

class Experiences(BaseModel):
    different_jobs: List[Experience]

class Education(BaseModel):
    school: str
    duration: str

class Educations(BaseModel):
    different_schools: List[Experience]

class Post(BaseModel):
    title: str
    subject: str
    date: str

class Posts(BaseModel):
    different_posts: List[Post]



def getMaires(poste, ville, attended_mode=False, driver=None):
    """
    Retrieves the profile of an interlocuteur given his job and the city.
    Output format: 
            [Experience(job="Vice-pr sident d l gu    l'eau,
                    l'assainissement et la prospective territoriale",
                    duration='Jul 2020 - Present'),
                    Experience(job="Adjoint au maire d l gu  aux solidarit s,
                    l'action sociale et   la lutte contre la pauvret ",
                    duration='Jul 2020 - Present'),
                    Experience(job='Vice-pr sident du CCAS de Dijon',
                    duration='Jul 2020 - Present'),
                    Experience(job='Pr sident',
                    duration='Jul 2020 - Present'),
                    Experience(job="charg  d' tudes et de missions",
                    duration='May 2015 - Sep 2020'),
                    Experience(job='Directeur de la Maison des Associations',
                    duration='Jan 2011 - Apr 2015'),
                    Experience(job='Charg  de mission Politique cyclable',
                    duration='Oct 2007 - Jan 2011')]

            different_schools=[Experience(job='Universit  de Bourgogne',
                    duration='2006 - 2007'),
                    Experience(job='IUT Dijon-Auxerre-Nevers',
                    duration='2005 - 2006'),
                    Experience(job='IUT Dijon-Auxerre-Nevers',
                    duration='2003 - 2005')]
    """
    if driver == None:
        driver = setup_selenium(False)
    search_tool = DuckDuckGoSearchRun(max_results = 2)
    results = search_tool.run("Quel est le nom et le prénom du "+poste+" de "+ville+" ?")
    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Analyses parfaitement les données qui te sont données pour en tirer tout le sens demandé."},
        {"role": "user", "content": "Donne moi le nom exact de "+poste+ " de "+ville+" sachant ce contexte: "+results+"""
            Ne répond que le nom exact demandé, pas de texte supplémentaire"""}
    ]
    )
    name = completion.choices[0].message.content
    res = fetch_html_selenium("https://www.linkedin.com/search/results/people/?keywords="+name+' ' +ville+"&origin=GLOBAL_SEARCH_HEADER&sid=jnZ", attended_mode, driver)
    if "Vous débutez sur LinkedIn" in res:
        print("Connectez vous a linkedin puis appuyez sur espace")
        keyboard.wait("space")
        print("Reprise du scrapping")
        return getMaires(poste, ville, attended_mode, driver)
    else:
        soup = BeautifulSoup(res, "html.parser")
        matching_link = soup.find("ul", role="list").find("li").find("a")["href"].split('?', 1)[0]
        experience_link = matching_link+'/details/experience/'
        education_link = matching_link+'/details/education/'
        # activity_link = matching_link+'/recent-activity/all/'
        main_soup = BeautifulSoup(fetch_html_selenium(matching_link, attended_mode, driver), 'html.parser')
        linkedin_name = main_soup.find("h1").get_text()
        name_parts = name.split()
        print(name)
        print(linkedin_name)
        for name_part in name_parts:
            if name_part.lower() not in linkedin_name.lower():
                print("Erreur, la personne n'a pas linkedin")
                return(None, None, None)
        exp_html = fetch_html_selenium(experience_link, attended_mode, driver)
        exp_soup = BeautifulSoup(exp_html, "html.parser")
        experience = exp_soup.find_all("div", class_="pvs-list__container")
        ed_html = fetch_html_selenium(education_link, attended_mode, driver)
        ed_soup = BeautifulSoup(ed_html, "html.parser")
        education = ed_soup.find_all("section", class_="artdeco-card pb3")
        # activ_html = fetch_html_selenium(activity_link, attended_mode, driver)
        # activ_soup = BeautifulSoup(activ_html, "html.parser")
        # activity = activ_soup.find_all("section", class_="artdeco-card pb3")
        completion_experience = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract all the relevant information."},
                {"role": "user", "content": """You are a detective specialized in profiling people. You are given a 
                 html code where there are information to find. You must return a precise summary of the experience of
                  the victim. You must isolate every experience, provide the name of the job (job), the period of time when
                 the victim had this job for every experience with a start date and an end date (duration). Here is the code containing all the experiences (jobs): """+f"""{experience}"""},
            ],
            response_format=Experiences,
        )
        completion_education = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract all the relevant information."},
                {"role": "user", "content": """You are a detective specialized in profiling people. You are given a 
                 html code where there are information to find. You must return a precise summary of the education of
                  the victim. You must isolate every education, provide the school mentioned (school) and the period when the victim studied 
                 there, with a start date and an end date (duration) for every education. Here is the code containing all the education divisions: """+f"""{education}"""},
            ],
            response_format=Educations,
        )
        # completion_activity = client.beta.chat.completions.parse(
        #     model="gpt-4o-2024-08-06",
        #     messages=[
        #         {"role": "system", "content": "Extract all the relevant information."},
        #         {"role": "user", "content": """You are a detective specialized in profiling people. You are given a 
        #          html code where there are information to find. You must return a precise summary of the posts of
        #           the victim. You must isolate the different posts, prepare a brief and accurate summary (subject), a title 
        #          (title) and retrieve the date of the post (date) for each one and return these elements for all the posts. 
        #          Here is the code where the posts are: """+f"""{activity}"""},
        #     ],
        #     response_format=Posts,
        # )
        driver.quit()
        return(completion_experience.choices[0].message.parsed, 
            #    completion_activity.choices[0].message.parsed,
               completion_education.choices[0].message.parsed)