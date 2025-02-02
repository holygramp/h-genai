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
                
                # Infos au début
                date_du_jour = datetime.today().strftime("%d/%m/%Y")
                st.markdown(f"""
                - Classification document: [C0] Tout public
                - Date du jour : {date_du_jour}
                - Code Postal: {data["id"]["insee"]}
                - Année de la mise à jour de la fiche: {data["id"]["year"]}
                - Nom de l'intercommunalité associée: **{data["inter"]["nom_epci"]}**
                - Remarque: les données affichées sont pour la ville. Pour obtenir les données de l'intercommunalité, cliquez sur le bouton affiché en fin de fiche.
                """)





                #Indicateurs financiers
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



                #1. Présentation générale
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
                        "text": "Répartition par type de logement",
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
                        "text": "Répartition par secteur",
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



                    
                



    








    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")


    #Pour ajouter des documents (si jamais)
    st.markdown("<h3 style='color:"+gray+";'>Option: téléverser des documents</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choisissez les documents à téléverser.",
        accept_multiple_files=True
    )

    df = pd.read_csv("h-genai/villes_sites.csv")
    path_list = []
    co2_eq_list = []
    # Bouton pour lancer l'opération
    if st.button("LAUNCH"):
        print ("ok")


# Run the application
if __name__ == "__main__":
    main()