import requests
from estrategia_base import EstrategiaBase

PUNTOS_REFERENCIA_URU = {
    "TACUAREMBÓ": (-32.166667, -55.5),
    "PAYSANDÚ": (-32.3217257, -58.0892136),
    "RÍO NEGRO": (-32.7257419, -57.387578),
    "FLORIDA": (-33.833333, -55.916667),
    "SAN JOSÉ": (-34.455, -56.616944),
    "MONTEVIDEO": (-34.9058916, -56.1913095),
    "COLONIA": (-34.4698592, -57.8433679),
    "RIVERA": (-30.900058, -55.5408151),
    "DURAZNO": (-33.0833329, -56.0833331),
    "TREINTA Y TRES": (-33.0, -54.25),
    "FLORES": (-33.6518845, -56.8393553),
    "ROCHA": (-34.0, -54.0),
    "SORIANO": (-33.4921266, -57.7893105),
    "MALDONADO": (-34.9087162, -54.9582718),
    "CERRO LARGO": (-32.333333, -54.333333),
    "SALTO": (-31.3571565, -57.004446),
    "LAVALLEJA": (-33.9971964, -54.9992242),
    "ARTIGAS": (-30.6170756, -56.9373451),
    "CANELONES": (-34.6222482, -55.9903797),
}

class EstrategiaUruguay(EstrategiaBase):
    def __init__(self):
        self.acronym = "uy"
        self.pais = "Uruguay"
        self.intentos_counter = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0
        }
        super().__init__()

    def procesar(self, row):
        departamento = row['Departamento']
        direccion_completa = row['direccion_completa']

        # Primer intento: llamar a la API de direcciones.ide.uy
        query = {
          "calle": direccion_completa,
          "departamento": departamento
        }
        
        lat, lon = self.obtener_lat_lon_geo_uy(query)
        if lat and lon:
            print("Exito en el primer intento")
            self.intentos_counter["1"] += 1
            return lat, lon, 1

        # Segundo intento: geopy usando dirección completa y departamento
        query = {
            "street": direccion_completa,
            "country": self.pais,
            "state": departamento
        }
        lat, lon = self.geolocalizar_con_geopy(query, self.acronym)
        if lat and lon:
            print("Exito en el segundo intento")
            self.intentos_counter["2"] += 1
            return lat, lon, 2
            
        # Tercer intento: usar geopy con barrio/localidad y departamento
        query = "Barrio " + str(row['BARRIO / LOCALIDAD']) + ", " + departamento + ", " + self.pais
        lat, lon = self.geolocalizar_con_geopy(query, self.acronym)
        if lat and lon:
            print("Exito en el tercer intento")
            self.intentos_counter["3"] += 1
            return lat, lon, 3

        # Si todo falla, usamos ubicación predeterminada del departamento
        if departamento in PUNTOS_REFERENCIA_URU:
            print("Exito en el cuarto intento")
            self.intentos_counter["4"] += 1
            referencia = PUNTOS_REFERENCIA_URU[departamento]
            return referencia[0], referencia[1], 4
        
        return None, None, 0  # No se pudo encontrar
    
    # https://www.gub.uy/infraestructura-datos-espaciales/tramites-y-servicios/servicios/servicio-direcciones-geograficas
    def obtener_lat_lon_geo_uy(self, query):
        url = "https://direcciones.ide.uy/api/v0/geocode/BusquedaDireccion"
        try:
            response = requests.get(url, params=query)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[0]['puntoY'], data[0]['puntoX']
            return None, None
        except Exception as e:
            print(f"Error en la API de Uruguay: {e}")
            return None, None
