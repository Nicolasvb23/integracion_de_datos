from estrategia_base import EstrategiaBase

class EstrategiaChile(EstrategiaBase):
  def __init__(self):
      self.acronym = "cl"
      self.pais = "Chile"
      self.intentos_counter = {
        "1": 0,
        "2": 0,
        "3": 0
      }
      super().__init__()

  def procesar(self, row):
    intento = 1
    
    # Intento 1 con comuna y provincia contra geopy
    # Hay muchos repetidos, usamos un hash para hacer menos requests.
    if self.network_cache.get(row['direccion_completa']):
      print("Usando cache de red para ", row['direccion_completa'])
      latitud = self.network_cache[row['direccion_completa']][0]
      longitud = self.network_cache[row['direccion_completa']][1]
      return latitud, longitud, intento
    else:
      latitud, longitud = self.geolocalizar_con_geopy(row['direccion_completa'], self.acronym)
      if latitud and longitud:
        self.network_cache[row['direccion_completa']] = (latitud, longitud)
        print("Exito en el primer intento")
        self.intentos_counter["1"] += 1

        return latitud, longitud, intento

    # Intento 2 solo con comuna contra geopy
    comuna = row['NOM_COM_RBD']
    if self.network_cache.get(comuna):
      print("Usando cache de red para ", comuna)
      latitud = self.network_cache[comuna][0]
      longitud = self.network_cache[comuna][1]
      return latitud, longitud, intento
    else:
      latitud, longitud = self.geolocalizar_con_geopy(comuna, self.acronym)
      if latitud and longitud:
        self.network_cache[comuna] = (latitud, longitud)
        print("Exito en el segundo intento")
        self.intentos_counter["2"] += 1
        return latitud, longitud, 2
    
    # Intento 3 solo con provincia contra geopy
    provincia = row['NOM_DEPROV_RBD']
    if self.network_cache.get(provincia):
      print("Usando cache de red para ", provincia)
      latitud = self.network_cache[provincia][0]
      longitud = self.network_cache[provincia][1]
      return latitud, longitud, intento
    else:
      latitud, longitud = self.geolocalizar_con_geopy(provincia, self.acronym)
      if latitud and longitud:
        self.network_cache[provincia] = (latitud, longitud)
        print("Exito en el tercer intento")
        self.intentos_counter["3"] += 1
        return latitud, longitud, 3
    
    return None, None, 0  # No se pudo encontrar
