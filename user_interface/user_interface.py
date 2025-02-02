#To run: streamlit run user_interface.py
import pandas as pd
import streamlit as st
import os
import time
import shutil
import base64
from datetime import datetime
import json
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
import plotly.express as px
import altair as alt
import requests
from docx import Document
from io import BytesIO


# Main function
def main():
    #Couleurs de la charte graphique de SFIL
    green = "#95BB20"
    verdigris = "#0DAEB1"
    blue = "#25367E"
    gray = "#666665"
    red = "#E20B17"

    # Logo SFIL
    try:
        with open("user_interface/logo_base64.txt", "r") as file:
            image_base64 = file.read().strip()
        
        # CSS pour centrer l'image
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{image_base64}" style="width:200px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    
    except FileNotFoundError:
        st.error("Le fichier 'user_interface/logo_base64.txt' est introuvable.")

    #Phrase d'accueil: Bienvenue sur AutoSfill
    st.markdown(f"""
        <h2 style='color:{verdigris}; text-align: center;'>
            Bienvenue sur AutoSfill !
        </h2>
        """, unsafe_allow_html=True)

    # Sélection de la ville
    df = pd.read_csv("./villes_sites.csv")
    cities = df["Ville"].tolist()
    st.markdown("<h3 style='color:"+gray+";'>Choisissez une commune:</h3>", unsafe_allow_html=True)
    selected_city = st.selectbox(
        "Pour quelle ville souhaitez-vous créer une fiche?",
        ["Sélectionnez une ville."] + cities
    )

    # Bouton "Générer une fiche client"
    if st.button("📄 Générer une fiche client"):
        if selected_city == "Sélectionnez une ville.":
            st.error("⚠️ Veuillez sélectionner une ville avant de générer une fiche client.")
        else:
            st.info(f"📦 Génération de la fiche pour **{selected_city}**...")

            # Affichage du spinner et attente de la création du fichier
            with st.spinner("⏳"):
                start_time = time.time()  # Début du compteur
                lambda_url = "https://caolsvkubnf7gcdpcpa5xktz5y0psruh.lambda-url.us-west-2.on.aws/city"
                # Envoie des informations à la Lambda
                # Fonction pour enregistrer la réponse dans un fichier JSON
                def enregistrer_reponse_json(response_data, filename="reponse_lambda.json"):
                    try:
                        # Enregistre le JSON dans un fichier local
                        with open(filename, 'w') as f:
                            json.dump(response_data, f, indent=4)
                        st.success(f"Réponse enregistrée dans {filename}")
                    except Exception as e:
                        st.error(f"Erreur lors de l'enregistrement du fichier: {str(e)}")

                def envoyer_a_lambda(data):
                    headers = {'Content-Type': 'application/json'}
                    try:
                        response = requests.get(lambda_url, headers=headers, data=data)
                        # Vérifie si la requête a réussi
                        if response.status_code == 200:
                            response_data = response.json()  # On récupère la réponse au format JSON
                            print('response_data')
                            enregistrer_reponse_json(response_data, filename=f"{selected_city}.json")
                        else:
                            st.error(f"Erreur: {response.status_code}, {response.text}")
                    except Exception as e:
                        st.error(f"Erreur lors de l'envoi de la requête: {str(e)}")

                envoyer_a_lambda({'city': f"{selected_city}"})

                #IMPORTANT: Appeler les fonctions des gars pour que ça cree le fichier ville_demandee.json
                #
                #
                #
                #
                #
                # Attente jusqu'à ce que le fichier existe
                file_name = f"user_interface/{selected_city}.json"
                # Attente de la création du fichier + compteur en temps réel
                elapsed_time = 0
                status_placeholder = st.empty()  # Placeholder pour afficher le temps

                while not os.path.exists(file_name):
                    elapsed_time = round(time.time() - start_time, 1)  # Arrondi à 0.1s
                    status_placeholder.markdown(f"Temps d'attente : **{elapsed_time}** sec...")
                    time.sleep(1)  # Vérification toutes les secondes
                
                # Temps total affiché après création
                total_time = round(time.time() - start_time, 1)
                st.success(f"✅ Fiche générée en **{total_time}** sec !")
                st.write("")
                st.write("")

                #Début de la fiche client
                st.markdown("<h1 style='color:"+blue+";'>Fiche Client : "+selected_city+".</h1>", unsafe_allow_html=True)
                
                # Ouvrir et lire le fichier JSON
                with open(file_name, "r") as f:
                    data = json.load(f)  # Charger le contenu du fichier
                


                # INFOS INITIALES
                date_du_jour = datetime.today().strftime("%d/%m/%Y")
                st.markdown(f"""
                - Classification document: [C0] Tout public
                - Date du jour : {date_du_jour}
                - Code Postal: {data["id"]["insee"]}
                - Année de la mise à jour de la fiche: {data["id"]["year"]}
                - Nom de l'intercommunalité associée: **{data["inter"]["nom_epci"]}**
                - Remarque: les données affichées sont pour la ville. Pour obtenir les données de l'intercommunalité, cliquez sur le bouton affiché en fin de fiche.
                """)







                #VISION RÉCAPITULATIVE
                st.markdown("<h3 style='color:"+verdigris+";'>Vision récapitulative</h3>", unsafe_allow_html=True)
                # Ajout d'un lien pour la source des données
                st.markdown(
                    f"<p style='color:{gray};'><a href=' https://www.data.gouv.fr/fr/datasets/comptes-des-communes-2016-2023/#/resources/7701d6a6-97e4-4938-9c38-a852cb14cfba' target='_blank' style='color:{gray};'> 🔗 Source</a></p>", 
                    unsafe_allow_html=True
                )
                # Tableau
                exercice = str(data["indicateurs_financiers"]["exer"])
                data_finance = {
                    'Vision récapitulative': ['Encours total budget principal (en M€)', '💡 Budget par habitant (en €)', 'Capacité de désendettement (en années)', 'Taux d’endettement (%)', 'Durée apparente de la dette (en années)'],
                    'Exercice': [{exercice}, {exercice}, {exercice}, {exercice}, {exercice}],
                    f'{selected_city}': [{data["indicateurs_financiers"]["encours_budget_principal"]}, {data["indicateurs_financiers"]["budget_par_habitant"]}, {data["indicateurs_financiers"]["capacite_desendettement"]}, {data["indicateurs_financiers"]["taux_endettement"]}, {data["indicateurs_financiers"]["duree_apparente_dette"]}],
                    'Moyenne Nationale': [' ', '1100', '5.7', '74', '10.3']
                }
                df = pd.DataFrame(data_finance)
                # Afficher le tableau 
                st.dataframe(df, hide_index=True)







                #1. PRESENTATION GENERALE
                st.markdown("<h3 style='color:"+verdigris+";'>1. Présentation générale</h3>", unsafe_allow_html=True)
                # Ajout d'un lien pour la source des données
                epci_code = data["inter"]["num_epci"]
                insee_code = data["id"]["insee"]
                st.markdown(
                    f"<p style='color:{gray};'><a href='https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-{epci_code}+COM-{insee_code}' target='_blank' style='color:{gray};'> 🔗 Source</a></p>", 
                    unsafe_allow_html=True
                )
                # Créer une liste avec la description et la valeur de chaque élément
                keys_to_display = ["population", "superficie", "densite", "chomage"]
                data_rows = []
                for key in keys_to_display:
                    description = data["data_description"].get(key, "Description non disponible")
                    value = data["presentations_generales"][key]
                    data_rows.append([description, {str(value)}])
                # Créer un DataFrame pandas
                df = pd.DataFrame(data_rows, columns=["Description", "Valeur"])
                # Afficher le tableau avec Streamlit
                st.dataframe(df, hide_index=True)

                # 1. Répartition par type de logement
                labels_logements = ['Résidences principales', 'Résidences secondaires', 'Logements vacants']
                sizes_logements = [data['presentations_generales']['part-resid-princ'], 
                                data['presentations_generales']['part-resid-second'], 
                                data['presentations_generales']['part-log-vac']]

                # 2. Répartition par secteur
                labels_secteurs = ['Agriculture', 'Industrie', 'Construction', 'Commerce', 'Administration']
                sizes_secteurs = [data['presentations_generales']['agriculture'], 
                                data['presentations_generales']['industrie'], 
                                data['presentations_generales']['construction'], 
                                data['presentations_generales']['commerce'], 
                                data['presentations_generales']['administration']]

                # Couleurs de la charte graphique
                colors = ["#95BB20", "#0DAEB1", "#25367E", "#666665", "#E20B17"]

                # Options pour le graphique circulaire des types de logement
                option_logements = {
                    "title": {
                        "text": "💡Répartition par type de logement",
                        "left": "center"
                    },
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{a} <br/>{b}: {c} ({d}%)"
                    },
                    "series": [
                        {
                            "name": "Logement",
                            "type": "pie",
                            "radius": "50%",
                            "data": [
                                {"value": sizes_logements[0], "name": labels_logements[0]},
                                {"value": sizes_logements[1], "name": labels_logements[1]},
                                {"value": sizes_logements[2], "name": labels_logements[2]},
                            ],
                            "label": {
                                "show": True,
                                "formatter": "{b}: {d}%"  # Afficher le pourcentage
                            },
                            "itemStyle": {
                                "color": "transparent"  # Pour que chaque couleur soit personnalisée
                            },
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                                }
                            }
                        }
                    ]
                }

                # Options pour le graphique circulaire des secteurs
                option_secteurs = {
                    "title": {
                        "text": "💡Répartition par secteur d'activité",
                        "left": "center"
                    },
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{a} <br/>{b}: {c} ({d}%)"
                    },
                    "series": [
                        {
                            "name": "Secteur",
                            "type": "pie",
                            "radius": "50%",
                            "data": [
                                {"value": sizes_secteurs[0], "name": labels_secteurs[0]},
                                {"value": sizes_secteurs[1], "name": labels_secteurs[1]},
                                {"value": sizes_secteurs[2], "name": labels_secteurs[2]},
                                {"value": sizes_secteurs[3], "name": labels_secteurs[3]},
                                {"value": sizes_secteurs[4], "name": labels_secteurs[4]},
                            ],
                            "label": {
                                "show": True,
                                "formatter": "{b}: {d}%"  # Afficher le pourcentage
                            },
                            "itemStyle": {
                                "color": "transparent"  # Pour que chaque couleur soit personnalisée
                            },
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                                }
                            }
                        }
                    ]
                }

                # Appliquer les couleurs personnalisées
                option_logements['series'][0]['data'][0]['itemStyle'] = {'color': colors[0]}
                option_logements['series'][0]['data'][1]['itemStyle'] = {'color': colors[1]}
                option_logements['series'][0]['data'][2]['itemStyle'] = {'color': colors[2]}

                option_secteurs['series'][0]['data'][0]['itemStyle'] = {'color': colors[4]}
                option_secteurs['series'][0]['data'][1]['itemStyle'] = {'color': colors[3]}
                option_secteurs['series'][0]['data'][2]['itemStyle'] = {'color': colors[2]}
                option_secteurs['series'][0]['data'][3]['itemStyle'] = {'color': colors[1]}
                option_secteurs['series'][0]['data'][4]['itemStyle'] = {'color': colors[0]}

                # Affichage des graphiques
                st_echarts(options=option_logements, height="400px")
                st_echarts(options=option_secteurs, height="400px")

                #Frise chronologique
                st.write("**Historique de la collectivité (réorganisations territoriales):**")
                frise_chronologique = data["presentations_generales"]["frise_chronologique"]
                df_frise = pd.DataFrame(frise_chronologique.items(), columns=['Année', 'Événement'])
                st.dataframe(df_frise, hide_index=True)








                # 2. PROJETS VERTS
                st.markdown("<h3 style='color:"+verdigris+";'>2. Projets verts</h3>", unsafe_allow_html=True)
                st.markdown("<h4 style='color:"+gray+";'>2.1. Explications</h4>", unsafe_allow_html=True)

                def colorer_score(val):
                    couleurs = {"A": "#278D30", "B": "#62AD4E", "C": "#EBDE37"}
                    return f"background-color: {couleurs.get(val, 'white')}; color: white"

                #Source: budget primitif
                # Ouvrir et lire le fichier JSON
                with open("directories.json", "r") as dir:
                    data_url = json.load(dir)  # Charger le contenu du fichier
                
                lien_BP = data_url[f"{selected_city}"][f"{selected_city}"+"_BP"]
                st.markdown(
                    f"<p style='color:{gray};'><a href='{lien_BP}' target='_blank' style='color:{gray};'> 🔗 Consultez le Budget primitif ici</a></p>", 
                    unsafe_allow_html=True
                )

                lien_DOB = data_url[f"{selected_city}"][f"{selected_city}"+"_DOB"]
                st.markdown(
                    f"<p style='color:{gray};'><a href='{lien_DOB}' target='_blank' style='color:{gray};'> 🔗 Consultez le Débat d'Orientation Budgétaire ici</a></p>", 
                    unsafe_allow_html=True
                )

                st.write("""Dans cette partie, nous présentons les projets prévus ou discutés. 
                            L'objectif est d'identifier les dépenses d’investissements éligibles.

    On évalue la probabilité que le projet se réalise avec un score:
        - A: sûr.
        - B: probable.
        - C: probable mais ne dépend pas du budget de la collectivité.
                        
    Les projets sont triés par:
        1. Thème (Energies renouvelables, etc.)
        2. Catégorie (Solaire, Eolien, etc.);
        3. Probabilité de réalisation ("projet" est une action prévue et budgettée; "tendance" est une action trouvée dans d'autres sources);
        4. Est-ce que l'action relève de la compétence de cette collectivité?""")
                st.image("user_interface/explication_projet.jpg")
                # Ajout d'un lien pour la source des données
                # Fonction pour convertir les projets verts en tableau structuré avec score
                def convertir_en_dataframe(data):
                    rows = []
                    # Itération sur les thèmes
                    for theme, categories in data['projets_verts'].items():
                        # Itération sur les catégories de chaque thème
                        for categorie, projets in categories.items():
                            # Si des projets existent pour cette catégorie
                            if projets:
                                for projet, infos in projets.items():
                                    score = " "
                                    if infos.get('type') == "projet":
                                        score = "A"
                                    elif infos.get('type') == "tendance":
                                        competence = infos.get('competence', 'non')
                                        score = "B" if competence == "oui" else "C"
                                    
                                    row = {
                                        'Thème': theme,
                                        'Catégorie': categorie,
                                        'Projet': projet,
                                        'Type': infos.get('type', 'Non défini'),
                                        'Échéance': infos.get('echeance', 'Non définie'),
                                        'Montant': infos.get('montant', 'Non défini'),
                                        'Compétence': infos.get('competence', 'Non définie'),
                                        'Score': score
                                    }
                                    rows.append(row)
                            else:
                                row = {
                                    'Thème': theme,
                                    'Catégorie': categorie,
                                    'Projet': 'Aucun projet identifié',
                                    'Type': ' ',
                                    'Échéance': ' ',
                                    'Montant': ' ',
                                    'Compétence': ' ',
                                    'Score': ' '
                                }
                                rows.append(row)
                    return pd.DataFrame(rows)

                # Convertir les données en dataframe
                df_projets = convertir_en_dataframe(data)

                # Afficher le tableau avec tous les projets verts
                st.markdown("<h4 style='color:"+gray+";'>2.2. Tableau</h4>", unsafe_allow_html=True)
                st.dataframe(df_projets.style.applymap(colorer_score, subset=["Score"]), hide_index=True)







                
                # 3. PROJETS SOCIAUX
                st.markdown("<h3 style='color:"+verdigris+";'>3. Projets sociaux</h3>", unsafe_allow_html=True)
                st.write("""On fait de même pour les projets sociaux.""")
                st.markdown(
                    f"<p style='color:{gray};'><a href='{lien_BP}' target='_blank' style='color:{gray};'> 🔗 Consultez le Budget primitif ici</a></p>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<p style='color:{gray};'><a href='{lien_DOB}' target='_blank' style='color:{gray};'> 🔗 Consultez le Débat d'Orientation Budgétaire ici</a></p>", 
                    unsafe_allow_html=True
                )

                # Fonction pour convertir les projets verts en tableau structuré avec score
                def convertir_en_dataframe_2(data):
                    rows = []
                    # Itération sur les thèmes
                    for theme, categories in data['projets_sociaux'].items():
                        # Itération sur les catégories de chaque thème
                        for categorie, projets in categories.items():
                            # Si des projets existent pour cette catégorie
                            if projets:
                                for projet, infos in projets.items():
                                    score = " "
                                    if infos.get('type') == "projet":
                                        score = "A"
                                    elif infos.get('type') == "tendance":
                                        competence = infos.get('competence', 'non')
                                        score = "B" if competence == "oui" else "C"
                                    
                                    row = {
                                        'Thème': theme,
                                        'Catégorie': categorie,
                                        'Projet': projet,
                                        'Type': infos.get('type', 'Non défini'),
                                        'Échéance': infos.get('echeance', 'Non définie'),
                                        'Montant': infos.get('montant', 'Non défini'),
                                        'Compétence': infos.get('competence', 'Non définie'),
                                        'Score': score
                                    }
                                    rows.append(row)
                            else:
                                row = {
                                    'Thème': theme,
                                    'Catégorie': categorie,
                                    'Projet': 'Aucun projet identifié',
                                    'Type': ' ',
                                    'Échéance': ' ',
                                    'Montant': ' ',
                                    'Compétence': ' ',
                                    'Score': ' '
                                }
                                rows.append(row)
                    return pd.DataFrame(rows)

                # Convertir les données en dataframe
                df_projets = convertir_en_dataframe_2(data)

                # Afficher le tableau avec tous les projets sociaux
                st.dataframe(df_projets.style.applymap(colorer_score, subset=["Score"]), hide_index=True)







               # 4. INTERLOCUTEURS
                st.markdown("<h3 style='color:"+verdigris+";'>4. Interlocuteurs</h3>", unsafe_allow_html=True)

                st.markdown(f'{data["interlocuteurs"]}')






               # 5. SITUATION FINANCIÈRE
                st.markdown("<h3 style='color:"+verdigris+";'>5. Analyse financière</h3>", unsafe_allow_html=True)
                # 5.1. 
                st.markdown("<h4 style='color:"+gray+";'>5.1. Budget primitif</h4>", unsafe_allow_html=True)
                st.write("**Tableau de présentation générale du budget**: Si cela vous intéresse de l'ajouter à la fiche, nous vous invitons à aller chercher le tableau sur ce lien:")
                st.markdown(
                        f"<p style='color:{gray};'><a href='{lien_BP}' target='_blank' style='color:{gray};'> 🔗 Lien du budget primitif</a></p>", 
                        unsafe_allow_html=True
                    )
                uploaded_files = st.file_uploader(
                    "Prenez une capture d'écran du tableau et déposez-la ci-dessous.",
                    accept_multiple_files=True
                )

                st.write("")
                exercice = str(data["indicateurs_financiers"]["exer"])
                st.write("**Tableau de flux financiers en "+exercice+"**:")

                st.markdown(
                    f"<p style='color:{gray};'><a href=' https://www.data.gouv.fr/fr/datasets/comptes-des-communes-2016-2023/#/resources/7701d6a6-97e4-4938-9c38-a852cb14cfba' target='_blank' style='color:{gray};'> 🔗 Source data.gouv.fr</a></p>", 
                    unsafe_allow_html=True
                )
                # Tableau
                data_finance = {
                    ' ': ['Fonctionnement (M€)', 'Investissement (M€)'],
                    'Dépenses': [f"{data['indicateurs_financiers']['depense_fonctionnement']}", f"{data['indicateurs_financiers']['depense_investissement']}"],
                    'Recettes': [f"{data['indicateurs_financiers']['recette_fonctionnement']}", f"{data['indicateurs_financiers']['recette_investissement']}"]
                }
                df = pd.DataFrame(data_finance)
                # Afficher le tableau 
                st.dataframe(df, hide_index=True)           



            # 5.2. Indicateurs de risques financiers
                st.markdown("<h4 style='color:"+gray+";'>5.2. Indicateurs de risques financiers</h4>", unsafe_allow_html=True)

                st.markdown(
                    f"<p style='color:{gray};'><a href=' https://www.data.gouv.fr/fr/datasets/comptes-des-communes-2016-2023/#/resources/7701d6a6-97e4-4938-9c38-a852cb14cfba' target='_blank' style='color:{gray};'> 🔗 Source</a></p>", 
                    unsafe_allow_html=True
                )
                # Tableau
                data_risques = {
                    ' ': ['Épargne de gestion (en €/hab)', 'Épargne brute (en €/hab)', 'Épargne nette (en €/hab)'],
                    f"{selected_city}": [f"{data['indicateurs_financiers']['epargne_gestion']}", f"{data['indicateurs_financiers']['epargne_brute']}",f"{data['indicateurs_financiers']['epargne_nette']}" ],
                    'Moyenne nationale': ['215', '193', '86']
                }
                df = pd.DataFrame(data_risques)
                # Afficher le tableau 
                st.dataframe(df, hide_index=True) 

                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")


# Run the application
if __name__ == "__main__":
    main()