# utils.py
# Andres Miguel Escolastico Lara. 23-EISN-2-056

import os
import json
import datetime

def create_project_folders():
    """
    Crea las carpetas necesarias para el proyecto.
    """
    folders = ["assets", "assets/images", "assets/music", "output"]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Carpeta creada (o ya existente): {folder}")

def save_story_data(story_data, theme, output_dir="output"):
    """
    Guarda los datos de la historia en un archivo JSON.
    
    Args:
        story_data (dict): Datos de la historia generada
        theme (str): Tema de la historia
        output_dir (str): Directorio de salida
    
    Returns:
        str: Ruta del archivo JSON guardado
    """
    # Asegurarse de que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear un nombre de archivo basado en el tema y la fecha/hora
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_theme = "".join(c if c.isalnum() else "_" for c in theme)
    filename = f"{safe_theme}_{timestamp}.json"
    file_path = os.path.join(output_dir, filename)
    
    # Añadir información adicional
    story_data["theme"] = theme
    story_data["generated_at"] = timestamp
    
    # Guardar los datos en formato JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, ensure_ascii=False, indent=4)
    
    return file_path

def estimate_narration_time(text, words_per_minute=150):
    """
    Estima el tiempo de narración en segundos basado en el número de palabras.
    
    Args:
        text (str): Texto a narrar
        words_per_minute (int): Velocidad de narración en palabras por minuto
    
    Returns:
        float: Tiempo estimado en segundos
    """
    words = len(text.split())
    minutes = words / words_per_minute
    seconds = minutes * 60
    return seconds