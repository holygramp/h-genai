from getInseeData import getInseeData
from getProfilesCV import getMaires
from getBanaticData import getBanaticData
import json

def presentationGeneralesVille(nom_ville):
    data = getInseeData(nom_ville)
    presentations_generales = data[1]["CITY"]
    frise = getBanaticData(nom_ville)[-1]
    presentations_generales["frise_chronologique"] = frise
    return(presentations_generales)
    
def presentationGeneralesEPCI(nom_ville):
    presentations_generales = getInseeData(nom_ville)[1]["EPCI"]
    data = getBanaticData(nom_ville)
    presentations_generales["frise_chronologique"] = data[-1]
    presentations_generales["dotation"] = data[3]
    presentations_generales["competences_facultatives"] = data[1]
    presentations_generales["competences_obligatoires"] = data[2]
    return(presentations_generales)

def interlocuteursVilleEtEPCI(poste, ville):
    name, experiences, educations = getMaires(poste, ville)
    
    # Create list for experiences
    experience_data = []
    for experience in experiences.different_jobs:
        experience_data.append({
            "Emploi": experience.job,
            "Durée": experience.duration
        })

    # Create list for educations
    education_data = []
    for education in educations.different_schools:
        education_data.append({
            "Ecole": education.school,
            "Durée": education.duration
        })

    # Create the complete data structure
    data = {
        "Nom": name,
        "Education": education_data,
        "Emplois": experience_data
    }

    # Convert to JSON
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    cleaned_output = json_str.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '')
    return cleaned_output

# print(presentationGeneralesVille("Dijon"))
# print(interlocuteursVilleEtEPCI("maire", "dijon"))
# print(presentationGeneralesEPCI("Dijon"))
