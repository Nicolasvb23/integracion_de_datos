import pandas as pd
import os
import requests

response_cache = {}

def transform_location(x, y):
  if (x, y) in response_cache:
    return response_cache[(x, y)]

  url = f'https://epsg.io/trans?s_srs=5382&t_srs=4326&x={x}&y={y}'
  response = requests.get(url)
  response_cache[(x, y)] = response
  return response

def transform_location_from_csv(ruta_csv):
  csv_to_transform = pd.read_csv(ruta_csv)
  print(f'Transformando archivo {os.path.basename(ruta_csv)}...')

  csv_to_transform['Latitud'] = None
  csv_to_transform['Longitud'] = None

  for i, row in csv_to_transform.iterrows():
    print(f'Procesando fila {i}...')
    response = transform_location(row['x'], row['y'])
    if response.status_code == 200:
      data = response.json()
      csv_to_transform.at[i, 'Latitud'] = data['y']
      csv_to_transform.at[i, 'Longitud'] = data['x']
    else:
      print(f'Error en fila {i}: {response.status_code}')
  
  csv_to_transform.to_csv(f'./output/{os.path.basename(ruta_csv)}', index=False)
  
  print(f'Archivo {os.path.basename(ruta_csv)} transformado con éxito')
  
transform_location_from_csv('./CSVs/ces_uy.csv')
transform_location_from_csv('./CSVs/ceip_uy.csv')
