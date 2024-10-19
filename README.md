# Proyecto para la asignatura Integración de Datos 2024 UdelaR
## Objetivo
Geolocalizar direcciones de Argentina, Uruguay y Chile, dando su ubicación a través de Latitud y Longitud.
Se usan mecanismos de fallback basados en la información que hay disponible en los CSVs que son de nuestro interés.

## Requerimientos
Tener `python` version `3.10.11` o mayores.

## Uso
Ejecutar `python3 geolocate/main.py` y seleccionar el CSV, las columnas que forman la dirección y el pais de referencia para mejorar la geolocalización.

## Uso para CSVs diferentes a los dados en el directorio CSVs
Es necesario cambiar dentro de los archivos de `estrategia_<acronimo_pais>` las columnas que están hardcodeadas. Por ejemplo, para el caso de Argentina, el `C. P.` que hace referencia al código postal además de `Departamento` y `Jurisdicción`
