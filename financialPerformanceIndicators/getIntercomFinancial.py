import json
import pandas as pd

def get_json_finance_inter(dataframe,epci_code, exer):
  """Retrieves data from the DataFrame and returns it as a JSON.

  Args:
    epci_code: The EPCI code to filter by.
    exer: The exer to filter by.

  Returns:
    A JSON object containing the data, or an error message if data is not found or if inputs are invalid.
  """
  try:
    exer = int(exer)  # Convert exer to integer
  except ValueError:
    return json.dumps({"error": "Invalid exer value. Please provide a valid year."})

  filtered_df = df_final[(dataframe['epci_code'] == epci_code) & (dataframe['exer'] == exer)]

  if filtered_df.empty:
    return json.dumps({"error": f"No data found for epci_code: {epci_code} and exer: {exer}"})

  data_dict = filtered_df.iloc[0].to_dict()

  # Handle potential NaN values
  for key, value in data_dict.items():
      if pd.isnull(value):
          data_dict[key] = None  # or any other desired representation for NaN

  return json.dumps(data_dict, ensure_ascii=False).encode('utf8')

test = get_json_finance_inter(df_final,242100410, 2023)
print(test.decode())  # This would print the JSON string (if data is found).