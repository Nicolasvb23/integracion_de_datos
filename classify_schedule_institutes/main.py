import pandas as pd

# Load the CSV file containing educational institution data
file_path = 'Instituciones.csv'
data = pd.read_csv(file_path)

# Function to check if any keywords exist in the description
def contains_keywords(description, keywords):
    return any(keyword.lower() in description.lower() for keyword in keywords)

# Functions to classify the type of institution based on the description
def classify_especial(description):
    keywords = ['Especial', 'Discapacidad', 'Autismo', 'Sordoceguera', 'Trastornos']
    return int(contains_keywords(description, keywords))

def classify_adultos(description):
  keywords = ['Adultos', 'Adulto', 'Adultez', 'Adultas', 'Adulta']
  return int(contains_keywords(description, keywords))

def classify_comun(description):
    # If it is not 'especial' or 'adultos', it is considered 'común'
    return int(not (classify_especial(description) or classify_adultos(description)) or contains_keywords(description, ['común', 'comun']))

def classify_inicial(description):
    keywords = ['Parvularia', 'Inicial', 'Preescolar']
    return int(contains_keywords(description, keywords))

def classify_primaria(description):
    keywords = ['Básica', 'Primaria', 'Educación General Básica']
    return int(contains_keywords(description, keywords))

def classify_secundaria(description):
    keywords = ['Media', 'Secundaria', 'Liceo', 'Preadolecencia', 'Adolescencia']
    return int(contains_keywords(description, keywords))

# Function to assign values to each classification category based on the description
def assign_values(row):
    row['Comun'] = classify_comun(row['Descripción'])
    row['Adultos'] = classify_adultos(row['Descripción'])
    row['Especial'] = classify_especial(row['Descripción'])
    row['Inicial'] = classify_inicial(row['Descripción'])
    row['Primaria'] = classify_primaria(row['Descripción'])
    row['Secundaria'] = classify_secundaria(row['Descripción'])
    return row

# Apply the classification function to each row in the dataframe
data = data.apply(assign_values, axis=1)

# Save the updated dataframe to a new CSV file
output_file_path = 'Instituciones_Actualizadas.csv'
data.to_csv(output_file_path, index=False)

# Output the path of the new CSV file
output_file_path
