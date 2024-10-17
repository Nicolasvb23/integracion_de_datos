import requests
from estrategia_base import EstrategiaBase

PUNTOS_REFERENCIA_URU = {
  "MONTEVIDEO": (-24.5662505, -62.1510371),
  "ARTIGAS": (-34.5900973, -58.4662985),
  "CANELONES": (-33.7779437, -58.5525623),
  "CERRO LARGO": (-36.9161456, -60.1670221),
  "COLONIA": (-31.4490399, -69.4195528),
  "DURAZNO": (-30.5216076, -68.9294279),
  "FLORES": (-34.6290748, -58.4634771),
  "FLORIDA": (-34.5322058, -58.4937312),
  "LAVALLEJA": (-34.6017151, -58.4356876),
  "MALDONADO": (-31.4141603, -64.1327023),
  "PAYSANDÚ": (-29.41830645, -66.8818875888676),
  "RÍO NEGRO": (-40.4811973, -67.6145911),
  "RIVERA": (-37.1605304, -63.2417835),
  "ROCHA": (-37.1460611, -60.9773386),
  "SALTO": (-34.2917828, -60.2544888),
  "SAN JOSÉ": (-26.8012401, -66.0698568),
  "SORIANO": (-34.6422783, -58.6660544),
  "TACUAREMBÓ": (-27.0351697, -55.2329551),
  "TREINTA Y TRES": (-34.6404554, -58.6655971)
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
                    return data[0]['puntoX'], data[0]['puntoY']
            return None, None
        except Exception as e:
            print(f"Error en la API de Uruguay: {e}")
            return None, None
