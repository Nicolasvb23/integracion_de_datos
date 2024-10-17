from geopy.geocoders import Nominatim
from global_geolocator import obtener_lat_long

class EstrategiaBase: 
  # Setear geolocator
  def __init__(self):
    # Inicializamos el geolocalizador con un user_agent personalizado
    self.geolocator = Nominatim(user_agent="GeoPyApp")

  def geolocalizar_con_geopy(self, direccion_completa, pais_referencia):
    """Método genérico para obtener latitud y longitud con geopy."""
    return obtener_lat_long(direccion_completa, pais_referencia, self.geolocator)

  def procesar(self, row, pais_referencia):
    intento = 1
    self.geolocalizar_con_geopy(row['direccion_completa'], pais_referencia), intento
  
