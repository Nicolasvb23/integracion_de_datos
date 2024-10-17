def obtener_lat_long(direccion, pais_referencia, geolocator):
    """Dada una dirección y un país de referencia, obtener su latitud y longitud."""
    try:
        print(f"Consultando coordenadas para: {direccion} en {pais_referencia}")
        location = geolocator.geocode(direccion, country_codes=pais_referencia)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error obteniendo coordenadas para {direccion}: {e}")
        return None, None
