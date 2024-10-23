import os
import threading
import pandas as pd
import time
from tkinter import Tk, Label, Button, filedialog, Listbox, MULTIPLE, StringVar, Radiobutton, END, messagebox, Toplevel
from estrategia_uy import EstrategiaUruguay
from estrategia_ar import EstrategiaArgentina
from estrategia_cl import EstrategiaChile

# Variables para almacenar las selecciones previas
selected_columns = []
selected_country = None

def seleccionar_estrategia(pais_referencia):
    """Ejecuta la estrategia de geolocalización correspondiente al país de referencia."""
    if pais_referencia == "uy":
        estrategia = EstrategiaUruguay()
    elif pais_referencia == "ar":
        estrategia = EstrategiaArgentina()
    elif pais_referencia == "cl":
        estrategia = EstrategiaChile()
    else:
        print("País de referencia no válido.")
        return None, None

    return estrategia

def procesar_csv(ruta_csv, columnas_direccion, pais_referencia, loading_window):
    """Procesa el CSV para añadir columnas de latitud y longitud."""
    # Directorio de salida
    output_dir = './output'

    # Asegurarse de que el directorio de salida existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ruta para el archivo temporal
    ruta_temporal = os.path.join(output_dir, f"temp_{os.path.basename(ruta_csv)}")

    # Cargar datos del CSV en un DataFrame de pandas
    if os.path.exists(ruta_temporal):
        # Si existe un archivo temporal, cargarlo
        df = pd.read_csv(ruta_temporal)
        print("Resumiendo desde el archivo temporal.")
    else:
        # Si no existe archivo temporal, cargar el archivo original
        df = pd.read_csv(ruta_csv)
        # Crear una columna de direcciones combinando las columnas especificadas. Solo tener en cuenta
        # las que no sean nulas y convertirlas a cadena
        df['direccion_completa'] = df[columnas_direccion].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
        # Añadir columnas para latitud, longitud y estado de procesamiento.
        # No borrar datos si es que ya hay columnas con esos nombres
        if 'Latitud' not in df.columns:
            df['Latitud'] = None
        if 'Longitud' not in df.columns:
            df['Longitud'] = None
        df['EstrategiaLatLong'] = None
        
    # Tamaño de los bloques para procesar
    batch_size = 100
    estrategia = seleccionar_estrategia(pais_referencia)

    # Procesar en bloques
    total_filas = len(df)
    for i in range(0, total_filas, batch_size):
        batch = df[i:i + batch_size]
        for idx, row in batch.iterrows():
            if pd.isnull(row['Longitud']) or pd.isnull(row['Latitud']):
                latitud, longitud, intento = estrategia.procesar(row)
                print(f"Procesando fila {idx}: {row['direccion_completa']} -> {latitud}, {longitud} (EstrategiaLatLong {intento})")
                df.at[idx, 'Latitud'] = latitud
                df.at[idx, 'Longitud'] = longitud
                df.at[idx, 'Intento'] = intento
            else:
                print(f"Saltando fila {idx}: {row['direccion_completa']} (ya procesada)")

        # Guardar el progreso en el archivo temporal
        df.to_csv(ruta_temporal, index=False)
        print(f"Progreso guardado: {min(i + batch_size, total_filas)} de {total_filas} filas procesadas.")
        print("Contador de tipos de intentos:", estrategia.intentos_counter)

    # Guardar el archivo final
    nombre_archivo = os.path.basename(ruta_csv)
    nombre_salida = os.path.join(output_dir, f"procesado_{nombre_archivo[:-4]}_{time.strftime('%Y%m%d-%H%M%S')}.csv")
    df.to_csv(nombre_salida, index=False)

    # Eliminar el archivo temporal
    os.remove(ruta_temporal)

    # Cerrar la ventana de carga
    loading_window.destroy()

    # Mostrar mensaje de éxito
    messagebox.showinfo("Éxito", f"Archivo procesado guardado en: {nombre_salida}")

def seleccionar_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo CSV."""
    ruta_csv = filedialog.askopenfilename(
        title="Seleccionar archivo CSV", 
        filetypes=(("Archivos CSV", "*.csv"),)
    )
    
    if ruta_csv:
        # Cargar el CSV y mostrar las columnas disponibles
        df = pd.read_csv(ruta_csv)
        columnas = list(df.columns)
        mostrar_columnas(ruta_csv, columnas)

def mostrar_columnas(ruta_csv, columnas):
    """Muestra una lista con las columnas del CSV para seleccionar las de dirección."""
    # Limpiar las listas antes de llenarlas
    listbox_columnas.delete(0, END)
    
    # Añadir las columnas disponibles a la lista
    for col in columnas:
        listbox_columnas.insert(END, col)
    
    # Restaurar la selección previa si existe
    for col in selected_columns:
        try:
            idx = listbox_columnas.get(0, END).index(col)
            listbox_columnas.select_set(idx)
        except ValueError:
            continue

    # Guardar la ruta del archivo seleccionado
    btn_procesar.config(state="normal")
    btn_procesar.config(command=lambda: iniciar_procesamiento(ruta_csv))

def guardar_selecciones_columnas(event):
    """Guarda las selecciones actuales de las columnas cuando el foco cambia."""
    global selected_columns
    selected_columns = [listbox_columnas.get(i) for i in listbox_columnas.curselection()]

def iniciar_procesamiento(ruta_csv):
    """Inicia el procesamiento en un hilo separado y muestra una ventana de carga."""
    # Guardar las selecciones actuales antes de procesar
    guardar_selecciones_columnas(None)

    # Obtener las columnas seleccionadas por el usuario
    columnas_seleccionadas = selected_columns
    pais_referencia = selected_country.get()

    # Validar las selecciones
    if len(columnas_seleccionadas) < 1:
        messagebox.showwarning("Advertencia", "Debes seleccionar al menos una columna para la dirección.")
        return

    if pais_referencia == "":
        messagebox.showwarning("Advertencia", "Debes seleccionar un país de referencia.")
        return

    # Crear una ventana de carga
    loading_window = Toplevel(ventana)
    loading_window.title("Procesando...")
    Label(loading_window, text="Procesando, por favor espera...").pack(pady=20)
    Label(loading_window, text="⏳").pack(pady=10)  # Aquí puedes personalizar el ícono de cargando

    # Ejecutar el procesamiento en un hilo separado
    threading.Thread(target=procesar_csv, args=(ruta_csv, columnas_seleccionadas, pais_referencia, loading_window)).start()

"""Crea la interfaz gráfica para la aplicación."""
# Crear la ventana principal
ventana = Tk()
ventana.title("Conversión de Direcciones a Coordenadas")
ventana.geometry("800x620")

# Etiquetas e instrucciones
Label(ventana, text="1. Selecciona un archivo CSV").pack(pady=10)

# Botón para seleccionar archivo CSV
btn_seleccionar = Button(ventana, text="Seleccionar CSV", command=seleccionar_archivo)
btn_seleccionar.pack(pady=5)

# Lista para mostrar las columnas disponibles del archivo CSV
Label(ventana, text="2. Selecciona las columnas que forman la dirección").pack(pady=10)
listbox_columnas = Listbox(ventana, selectmode=MULTIPLE, width=50, height=10)
listbox_columnas.pack(pady=5)

# Evento para guardar las selecciones cuando se interactúa con el Listbox
listbox_columnas.bind("<FocusOut>", guardar_selecciones_columnas)

# Punto de referencia para la precisión de la geolocalización
Label(ventana, text="3. Selecciona el país de referencia").pack(pady=10)

# Variable para almacenar la selección del país (valor predeterminado: None)
selected_country = StringVar()
selected_country.set(None)

# Radiobuttons para seleccionar el país a
Radiobutton(ventana, text="Uruguay (uy)", variable=selected_country, value="uy").pack(pady=5)
Radiobutton(ventana, text="Argentina (ar)", variable=selected_country, value="ar").pack(pady=5)
Radiobutton(ventana, text="Chile (cl)", variable=selected_country, value="cl").pack(pady=5)

# Botón para procesar el archivo CSV (desactivado al principio)
btn_procesar = Button(ventana, text="Procesar CSV", state="disabled")
btn_procesar.pack(pady=20)

# Ejecutar la ventana
ventana.mainloop()
