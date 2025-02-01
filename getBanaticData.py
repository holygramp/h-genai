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
from coreScrapingFunctions import setup_selenium
from getInseeData import getInseeCode


def getTypeEPCI(ville):
    """
    Retrieves the type of EPCI (CA, CC, CU, M) of a city given it's name
    Output format: string
    """
    name_EPCI = requests.get("https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-communes/records?where=com_name%20%3D%20%22"+ville+"%22&limit=1").json()['results'][0]["epci_name"]
    type_EPCI = requests.get("https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-gfp/records?select=exer%2C%20epci_name%2C%20nat_juridique&where=nom_23%20%3D%20%22"+name_EPCI+"%22&limit=1").json()['results'][0]['nat_juridique']
    if type_EPCI == "M":
        return("Métropole")
    elif type_EPCI == "CU":
        return("Communauté urbaine")
    elif type_EPCI == "CA":
        return("Communauté d'agglomération")
    elif type_EPCI == "CC":
        return("Communauté de communes")
    elif type_EPCI == "MET69":
        return("Métropole de Lyon")
    elif type_EPCI == "EPT":
        return("Etablissement public territorial")
    else:
        print("Erreur, type d'EPCI non valide")
        return None


def getBanaticData(ville, driver=None, attended_mode=False):
    """
    Retrieves :
        - EPCI president name,
        - Compétences facultatives,
        - Compétences obligatoires,
        - Dotation,
        - Frise chronologique,
    for a given city name.

    Output format:
            ('BIANCHI Olivier',
             
               {"Production, réseaux et distribution d'énergie": ['Eclairage public'], 'Développement et
                aménagement éducatif, sportif et culturel ': ['Construction, reconstruction, aménagement, entretien et fonctionnement
                des lycées (accueil, restauration, hébergement, entretien général et technique)', 'Construction, reconstruction,
                aménagement, entretien et fonctionnement des collèges (accueil, restauration, hébergement, entretien général et
                technique)', 'Activités culturelles ou socioculturelles', 'Activités sportives'], 'Transports et voirie': ["Mise en
                place d'itinéraires cyclables"], 'Logement et habitat': ['Délégation des aides à la pierre - Compétences insécables (IV
                Art.L.301-5-1 CCH) - Etat', 'Délégation des aides à la pierre - Compétences sécables (V Art.L.301-5-1 CCH) - Etat'],
                'Autres': ['Fourrière automobile', "AutresAfficher plus d'informations"]}, 
                
                {"Production, réseaux et distribution
                d'énergie": ["Concession de la distribution publique d'électricité", 'Concession de la distribution publique de gaz',
                'Création, aménagement, entretien et gestion des réseaux de chaleur ou de froid urbains', "Soutien aux actions de
                maîtrise d'énergie ", "Création et entretien des infrastructures de charge nécessaires à l'usage des véhicules
                électriques ou hybrides rechargeables, en application de l'article L2224-37 du CGCT", 'Contribution à la transition
                énergétique'], 'Eau et assainissement': ['Gestion des eaux pluviales urbaines'], 'Environnement, développement durable
                et cadre de vie': ["Mise en place d'une zone à faible émissions mobilité (ZFE-m) (L. 2213-4-1 du CGCT)", "GEMAPI :
                Aménagement d'un bassin ou d'une fraction de bassin hydrographique (L. 211-7 1° du code de l'environnement)", "GEMAPI :
                Entretien et aménagement d'un cours d'eau, canal, lac ou plan d'eau (L. 211-7 2° du code de l'environnement)", "GEMAPI :
                Défense contre les inondations et contre la mer (L. 211-7 5° du code de l'environnement)", "GEMAPI : Protection et
                restauration des sites, des écosystèmes aquatiques, des zones humides et des formations boisées riveraines (L. 211-7 8°
                du code de l'environnement)", "Autorité concessionnaire de l'Etat pour les plages, dans les conditions prévues à
                l'article L. 2124-4 du code général de la propriété des personnes publiques.", "Elaboration et adoption du plan
                climat-air-énergie territorial en application de l'article L. 229-26 du code de l'environnement", 'Exercice de la
                compétence collecte des déchets ménagers et assimilés', 'Exercice de la compétence traitement des déchets ménagers et
                assimilés', 'Lutte contre les nuisances sonores', "Lutte contre la pollution de l'air"], 'Services funéraires':
                ['Création, gestion, extension et translation des cimetières et sites cinéraires', 'Création, gestion et extension des
                crématoriums'], 'Politique de la ville / Prévention de la délinquance': ["Elaboration du diagnostic du territoire et
                définition des orientations du contrat de ville, animation et coordination des dispositifs contractuels de développement
                urbain, de développement local et d'insertion économique et sociale ainsi que des dispositifs locaux de prévention de la
                délinquance ; programmes d'actions définis dans le contrat de ville"], 'Développement et aménagement économique':
                ["Actions de développement économique dans les conditions prévues à l'article L. 4251-17 ; politique locale du commerce
                et soutien aux activités commerciales", "Création, aménagement, entretien et gestion de zones d'activité industrielle,
                commerciale, tertiaire, artisanale, touristique, portuaire ou aéroportuaire"], 'Développement touristique': [],
                'Développement et aménagement éducatif, sportif et culturel ': ["Construction, aménagement, entretien et fonctionnement
                d'équipements culturels et sportifs", "Programme de soutien et d'aides aux établissements d'enseignement supérieur et de
                recherche et aux programmes de recherche"], "Aménagement de l'espace communautaire ou métropolitain": ["Schéma de
                cohérence territoriale (SCOT) (Art. L. 143-16 code de l'urbanisme)", "Schéma de secteur (Art. L. 173-1 du code de
                l'urbanisme)", "Plan local d'urbanisme et document d'urbanisme en tenant lieu (Art. L. 153-1 du code de l'urbanisme)",
                "Définition, création et réalisation d'opérations d'aménagement d'intérêt communautaire au sens de l'article L.300-1 du
                code de l'urbanisme (les ZAC entrent dans cette catégorie)", "Constitution de réserves foncières (articles L.210-1 et
                L.221-1 du code de l'urbanisme)", 'Actions de valorisation du patrimoine naturel et paysager'], 'Autorité organisatrice
                de la mobilité au sens des articles L. 1231-1, L. 1231-8 et L. 1231-14 à L. 1231-16 du code des transports': [],
                'Transports et voirie': ["Participation à la gouvernance et à l'aménagement des gares situées sur le territoire
                métropolitain", 'Création, aménagement, entretien de la voirie communale', 'Signalisation, abris de voyageurs, parcs et
                aires de stationnement', 'Plans de mobilité'], 'Logement et habitat': ["Programme local de l'habitat", 'Action et aide
                financière en faveur du logement social', 'Action en faveur du logement des personnes défavorisées', "Opération
                programmée d'amélioration de l'habitat (OPAH)", 'Amélioration du parc immobilier bâti', "Actions de réhabilitation et
                résorption de l'habitat insalubre"], 'Accueil des gens du voyage': ["Aménagement, entretien et gestion des aires
                d'accueil des gens du voyage et des terrains familiaux locatifs"], 'Autres': ['Abattoirs publics', "Marchés d'intérêt
                national, halles, foires et marchés", "Centre de première intervention des services locaux d'incendie et de secours (L.
                1424-36-4)", "Service public de défense extérieure contre l'incendie", "Réseaux et services locaux de communications
                électroniques d'initiative publique au sens de l'article L 1425-1 CGCT"]}, 
                
                '31755301', 
                
                {'Le 24/12/1999': "Création d'un groupement", 'Le 27/12/2017': 'Création de la métropole "Clermont-Auvergne Métropole" au 01 01 2018'})
    """
    sys.stdout.reconfigure(encoding='utf-8')
    insee_code, epci_code = getInseeCode(ville)
    if insee_code == None:
        return None
    res = requests.get("https://www.banatic.interieur.gouv.fr/intercommunalite/"+epci_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    p_balises = soup.find_all("p", class_="fr-badge fr-badge--blue-cumulus")
    for p in p_balises:
        if p.text.strip() == "Président":
            # Trouver la balise <td> juste avant l'élément <p> contenant "président"
            span_before = p.find_previous("span")
            president = span_before.get_text()
    if driver == None:
        driver = setup_selenium(False)
    driver.get("https://www.banatic.interieur.gouv.fr/intercommunalite/"+epci_code)
    time.sleep(5)
    buttons = driver.find_elements(By.CLASS_NAME, "fr-accordion__btn")

    # Itérer et cliquer sur chaque bouton
    for button in buttons:
        button.click()
    time.sleep(2)
    # Récupérer l'HTML complet de la page après avoir cliqué sur les boutons
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    comp_facultatives = soup.find("div", id="accordeon-competences-facultatives")
    result_facultatives = {}

    # Trouver toutes les balises <p> dans cette div
    p_tags = comp_facultatives.find_all("p", class_="ListeCompetences_titreCategorie___6AxT")

    # Pour chaque balise <p>, trouver les <li> à l'intérieur et créer le JSON
    for p_tag in p_tags:
        # Trouver toutes les balises <li> qui suivent cette balise <p> dans le même parent
        li_tags = p_tag.find_next("ul").find_all("li", class_=["ListeCompetences_competence__T_EIN", "ListeCompetences_transfertsCompetence__eddVU"])  # Trouve l'élément <ul> suivant et ses <li>
        
        # Extraire les textes des balises <li>
        li_contents = [li.get_text() for li in li_tags]
        
        # Ajouter cette information au dictionnaire (contenu_p : liste des contenus_li)
        result_facultatives[p_tag.get_text()] = li_contents

    comp_facultatives = soup.find("div", id="accordeon-competences-obligatoires")
    result_obligatoires = {}
    # Trouver toutes les balises <p> dans cette div
    p_tags = comp_facultatives.find_all("p", class_="ListeCompetences_titreCategorie___6AxT")

    # Pour chaque balise <p>, trouver les <li> à l'intérieur et créer le JSON
    for p_tag in p_tags:
        # Trouver toutes les balises <li> qui suivent cette balise <p> dans le même parent
        li_tags = p_tag.find_next("ul").find_all("li", class_=["ListeCompetences_competence__T_EIN", "ListeCompetences_transfertsCompetence__eddVU"])  # Trouve l'élément <ul> suivant et ses <li>
        
        # Extraire les textes des balises <li>
        li_contents = [li.get_text() for li in li_tags]
        
        # Ajouter cette information au dictionnaire (contenu_p : liste des contenus_li)
        result_obligatoires[p_tag.get_text()] = li_contents
    dotation = soup.find("span", class_="GraphiqueCirculaire_graphiqueCirculaire__total_valeur__vJNdF").get_text()

    event_tags = soup.find_all("div", class_=["TuileEvenement_evenement__ayvfl", "TuileEvenement_evenement__ayvfl TuileEvenement_evenement_creation__Xe7VS"])
    result_frise = {}
    for event_tag in event_tags:
        titre_element = event_tag.find_next("div", class_="TuileEvenement_evenement__titre__gCUbq")
        if titre_element and titre_element.get_text().startswith(("Création", "Adhésion")):
            result_frise[event_tag.find("p").get_text()] = event_tag.find("div", class_="TuileEvenement_evenement__titre__gCUbq").get_text()
    driver.quit()
    return president, result_facultatives, result_obligatoires,"".join([item.replace("\u202f", "") for item in dotation]) , result_frise
    
print(getBanaticData("Clermont-Ferrand"))