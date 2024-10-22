from geopy.geocoders import Nominatim
from global_geolocator import obtener_lat_long

class EstrategiaBase: 
  # Setear geolocator
  def __init__(self):
    # Inicializamos el geolocalizador con un user_agent personalizado
    self.geolocator = Nominatim(user_agent="GeoPyApp")
    self.network_cache = {}

  def geolocalizar_con_geopy(self, direccion_completa, pais_referencia):
    """Método genérico para obtener latitud y longitud con geopy."""
    return obtener_lat_long(direccion_completa, pais_referencia, self.geolocator)

  def procesar(self, row, pais_referencia):
    intento = 1
    if self.network_cache.get(row['direccion_completa']):
      print("Usando cache de red para ", row['direccion_completa'])
      latitud = self.network_cache[row['direccion_completa']][0]
      longitud = self.network_cache[row['direccion_completa']][1]
      return latitud, longitud, intento
    else:
      latitud, longitud = self.geolocalizar_con_geopy(row['direccion_completa'], pais_referencia)
      if latitud and longitud:
        self.network_cache[row['direccion_completa']] = (latitud, longitud)
        return latitud, longitud, intento
      else:
        return None, None, 0  # No se pudo encontrar    
  
