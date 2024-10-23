from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

geolocator = Nominatim(user_agent="GeoPyApp")

def geolocalizar(ciudad):
  """Obtener latitud y longitud de una ciudad."""
  print("Localizando", ciudad)
  location = geolocator.geocode(ciudad, country_codes="uy")
  if location:
    print("Encontrado", ciudad)
    return location.latitude, location.longitude
  else:
    print("No encontrado", ciudad)
    return None, None

# Mapa de ciudades agrupadas por departamento
DEPARTAMENTOS_UY = {
  "Montevideo": ["Montevideo, Montevideo"],
  "Salto": ["Salto, Salto"],
  "Canelones": ["Ciudad de la Costa", "Las Piedras", "Barros Blancos", "Pando", "Salinas", "18 de Mayo", "La Paz", "Canelones, Canelones", "Santa Lucia", "Progreso", "Paso Carrasco", "Joaquin Suarez", "General Liber Seregni", "Toledo", "Parque del Plata", "Atlantida", "San Ramon", "Sauce", "Tala"],
  "Paysandu": ["Paysandu, Paysandu", "Guichon"],
  "Maldonado": ["Maldonado, Maldonado", "Punta del Este", "Piriapolis", "San Carlos", "Pan de Azucar"],
  "Rivera": ["Rivera, Rivera", "Tranqueras"],
  "Cerro largo": ["Melo", "Rio Branco"],
  "Artigas": ["Artigas, Artigas", "Bella Union"],
  "Soriano": ["Mercedes", "Dolores", "Cardona"],
  "Lavalleja": ["Minas", "Jose Pedro Varela"],
  "San Jose": ["San Jose de Mayo", "Ciudad del Plata", "Libertad"],
  "Durazno": ["Durazno, Durazno", "Sarandi del Yi"],
  "Florida": ["Florida, Florida", "Sarandi Grande"],
  "Treinta y tres": ["Treinta y Tres, Treinta y tres"],
  "Colonia": ["Colonia del Sacramento", "Carmelo", "Nueva Helvecia", "Juan Lacaze", "Rosario", "Nueva Palmira", "Tarariras"],
  "Rocha": ["Rocha, Rocha", "Chuy", "Lascano", "Castillos", "La Paloma"],
  "Rio negro": ["Fray Bentos", "Young"],
  "Flores": ["Trinidad"],
  "Tacuarembo": ["Tacuarembo, Tacuarembo", "Paso de los Toros"]
}

LAT_LONG_CIUDADES = {
  ciudad: geolocalizar(ciudad)
  for ciudades in DEPARTAMENTOS_UY.values()
  for ciudad in ciudades
}

print(LAT_LONG_CIUDADES)

def medir_distancia(lat1, lon1, lat2, lon2):
  """Medir la distancia entre dos puntos geográficos."""
  return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def procesar_csv(ruta_csv):
  """Procesar un archivo CSV y medir distancias."""
  contador = 0
  df = pd.read_csv(ruta_csv)
  df['Ambito'] = None

  for idx, row in df.iterrows():
    latitud = float(row['Latitud'])
    longitud = float(row['Longitud'])
    departamento = row['Departamento'].capitalize()
    departamento = departamento.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    nombre = row['Nombre']
    
    print("Departamento a buscar", departamento)
    ciudades = DEPARTAMENTOS_UY.get(departamento, [])
    encontrado = False
    
    print("Buscando ciudad cercana para", nombre)
    print("Potenciales ciudades:", ciudades)
    for ciudad in ciudades:
      lat_ciudad, lon_ciudad = LAT_LONG_CIUDADES[ciudad]
      if lat_ciudad is not None and lon_ciudad is not None:
        distancia = medir_distancia(latitud, longitud, lat_ciudad, lon_ciudad)
        print("Distancia a", ciudad, ":", distancia)
        if distancia <= 15:
          df.at[idx, 'Ambito'] = 'Urbano'
          encontrado = True
          break
    
    if not encontrado:
      print(nombre)
      contador += 1
      df.at[idx, 'Ambito'] = 'Rural'
    print("\n")

  print(f"Total de registros sin ciudad cercana: {contador}")
  df.to_csv(ruta_csv[:-4] + "_ambito.csv", index=False)

# Ejemplo de uso
ruta_csv = "../output/privados_uy.csv"
procesar_csv(ruta_csv)

ruta_csv = "../output/ces_uy.csv"
procesar_csv(ruta_csv)
