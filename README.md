# AutoSfill

**AutoSfill** est un outil qui automatise la création de fiches clients pour Sfil. Ces fiches sont basées sur des données publiques collectées sur Internet, par Google dork, scrapping et API, sur des sources fiables de données (cf. architecture). 

L'application permet de générer une fiche complète et standardisée sur une application Streamlit pour chaque commune et intercommunalité de plus de 80.000 habitants, offrant un aperçu de la situation financière, des projets en cours, et des interlocuteurs privilégiés de cette collectivité.



## Description

**AutoSfill** permet de générer automatiquement des fiches clients détaillées à partir des informations publiques disponibles sur Internet. 

Les utilisateurs peuvent sélectionner une commune et obtenir une fiche client générée automatiquement.

La fiche comprend une présentation générale, une analyse financière, des informations sur les interlocuteurs privilégiés et  des détails sur les projets à venir dans 2 thématiques: projets verts et projets sociaux.



### Fonctionnalités principales de l'application Streamlit

1. **Page d'accueil pour sélectionner la ville** :  
   L'utilisateur peut choisir une commune parmi une liste d'exemples fournie. Le nom de la ville est ensuite utilisé pour générer une fiche.

2. **Génération de la fiche client** :  
   En cliquant sur le bouton "Générer une fiche client", une fiche détaillée de la ville sélectionnée est générée. Si aucune ville n'est choisie, un message d'erreur s'affiche.

3. **Affichage dynamique des informations de la fiche** :  
   Après la génération de la fiche, l'application affiche plusieurs informations clés :  
   0. Informations générales (code postal, intercommunalité, date de mise à jour, etc.) et un tableau récapitulatif des indicateurs financiers (budget, endettement, etc.).
   1. Présentation générale: des données démographiques et socio-économiques sur la collectivité (population, superficie, chômage, etc.).
   2. Détails sur les projets verts.
   3. Détails sur les projets sociaux.
   4. CV des interlocuteurs privilégiés (par défaut, le Maire).
   5. Une analyse financière (budget primitif, flux financiers, risques).


## Installation

1. Clonez le repository ou téléchargez les fichiers nécessaires.
2. Créez un environnement virtuel (recommandé) :
   python -m venv venv
3. Activez l'environnement virtuel :
    Sur macOS/Linux : source venv/bin/activate
    Sur Windows :venv\Scripts\activate
4. Installez les dépendances :
    pip install pandas streamlit matplotlib plotly altair requests python-docx streamlit-echarts

## Utilisation

Lancez l'application Streamlit avec la commande suivante :
streamlit run user_interface.py

## Configuration
- L'application utilise villes_sites.csv, departements-france.csv, logo_base64.txt, explication_projet.jpg

Assurez-vous que ces fichiers soient présents dans le répertoire ./ avec les bonnes données pour que la sélection des villes fonctionne.