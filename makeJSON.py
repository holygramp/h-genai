from getInseeData import getInseeData
from getProfilesCV import getMaires
import json

def presentationGeneralesVille(nom_ville):
    presentations_generales = getInseeData(nom_ville)[1]["CITY"]
    return(presentations_generales)
    
def presentationGeneralesEPCI(nom_ville):
    presentations_generales = getInseeData(nom_ville)[1]["EPCI"]
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

