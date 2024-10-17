import requests
from estrategia_base import EstrategiaBase

PUNTOS_REFERENCIA = {
  "Ciudad de Buenos Aires": (-34.6083696, -58.4440583),
  "Buenos Aires": (-34.6083696, -58.4440583),
  "Catamarca": (-27.1910825, -67.105374),
  "Córdoba": (-31.4166867, -64.1834193),
  "Corrientes": (-28.99565115, -57.81245796667342),
  "Chaco": (-26.3829647, -60.8816092),
  "Chubut": (-43.7128356, -68.7461817),
  "Entre Ríos": (-31.6252842, -59.3539578),
  "Formosa": (-24.5955306, -60.4289718),
  "Jujuy": (-23.3161458, -65.7595288),
  "La Pampa": (-37.2314643, -65.3972948),
  "La Rioja": (-29.9729781, -67.0487944),
  "Mendoza": (-34.787093049999996, -68.43818677312292),
  "Misiones": (-26.737224, -54.4315257),
  "Neuquén": (-38.3695057, -69.832275),
  "Río Negro": (-40.4811973, -67.6145911),
  "Salta": (-24.7892946, -65.4103194),
  "San Juan": (-31.5370909, -68.5251802),
  "San Luis": (-33.2762202, -65.9515546),
  "Santa Cruz": (-48.5693327, -70.1606767),
  "Santa Fe": (-30.3154739, -61.1645076),
  "Santiago del Estero": (-27.6431016, 63.5408542),
  "Tucumán": (-26.8303703, 65.2038133),
  "Tierra del Fuego": (-54.4071064, -67.8974895)
}

class EstrategiaArgentina(EstrategiaBase):
    def __init__(self):
        self.acronym = "ar"
        self.pais = "Argentina"
        self.intentos_counter = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0
        }
        super().__init__()

    def procesar(self, row):
        direccion = row['direccion_completa']
        provincia = row['Jurisdicción']
        departamento = row['Departamento']

        # Primer intento: usar la API de georef en Argentina
        query = {
            "direccion": direccion,
            "provincia": provincia,
            "departamento": departamento,
            "max": 1
        }
        lat, lon = self.obtener_lat_long_geo_arg(query)
        if lat and lon:
            print("Exito en el primer intento")
            self.intentos_counter["1"] += 1
            return lat, lon, 1
        
        # Segundo intento: usar geopy con provincia y domicilio completo
        query = {
            "street": direccion,
            "country": self.pais,
            "state": provincia
        }
        lat, lon = self.geolocalizar_con_geopy(query, self.acronym)
        if lat and lon:
            print("Exito en el segundo intento")
            self.intentos_counter["2"] += 1
            return lat, lon, 2        

        # Tercer intento: usar el código postal con geopy
        query = {
            "postalcode": row['C. P.'],
            "country": self.pais,
        }
        
        lat, lon = self.geolocalizar_con_geopy(query, self.acronym)
        if lat and lon:
            print("Exito en el tercer intento")
            self.intentos_counter["3"] += 1
            return lat, lon, 3

        # Cuarto intento: usar ubicación por defecto de la provincia
        if provincia in PUNTOS_REFERENCIA:
            print("Exito en el cuarto intento")
            self.intentos_counter["4"] += 1
            latitud, longitud = PUNTOS_REFERENCIA[provincia]
            return latitud, longitud, 4

        return None, None, 0  # No se pudo encontrar
    
    # https://www.argentina.gob.ar/datos-abiertos/georef/openapi#/Recursos/get_direcciones
    def obtener_lat_long_geo_arg(self, query):
        url = "https://apis.datos.gob.ar/georef/api/direcciones"
        response = requests.get(url, params=query)
        if response.status_code == 200:
            data = response.json()
            if data['cantidad'] > 0:
                latitud = data['direcciones'][0]['ubicacion']['lat']
                longitud = data['direcciones'][0]['ubicacion']['lon']
                return latitud, longitud
        return None, None
