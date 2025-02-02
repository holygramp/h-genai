# import boto3 
import json
from dorkingFunctions import getAllDOB, getAllBudgetsPrimitifs
import pandas as pd
import os
import sys

# df = pd.read_csv("h-genai/villes_sites.csv")

# # Déterminer la taille de chaque sous-fichier
# chunk_size = len(df) // 10

# for i in range(10):
#     # Déterminer les indices de début et de fin pour chaque chunk
#     start_idx = i * chunk_size
#     # Le dernier fichier prend les lignes restantes
#     end_idx = (i + 1) * chunk_size if i < 9 else len(df)
    
#     # Créer le sous-DataFrame
#     df_chunk = df.iloc[start_idx:end_idx]
    
#     # Sauvegarder chaque chunk dans un nouveau fichier CSV
#     df_chunk.to_csv(f"fichier_part_{i + 1}.csv", index=False)

# Initialize directories dictionary
directories = {}

# Load existing data if file exists
if os.path.exists("directories.json"):
    with open("directories.json", "r", encoding="utf-8") as f:
        directories = json.load(f)

# Process each file
for file_num in range(9, 11):
    try:
        # Use string formatting for file names
        filename = f'fichier_part_{file_num}.csv'
        
        # Get links and data
        DOB_links = getAllDOB(filename)
        BP_links = getAllBudgetsPrimitifs(filename)
        df = pd.read_csv(filename)
        villes = df['Ville'].tolist()

        # Add data for each city
        for i in range(len(DOB_links)):
            ville = villes[i]
            directories[ville] = {
                f"{ville}_DOB": DOB_links[i],
                f"{ville}_BP": BP_links[i]
            }
        
        # Save the updated data after each file is processed
        with open("directories.json", "w", encoding="utf-8") as f:
            json.dump(directories, f, ensure_ascii=False, indent=4)
            
        print(f"Processed file {filename}")
        
    except Exception as e:
        print(f"Error processing file {file_num}: {str(e)}")

