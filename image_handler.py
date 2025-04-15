# image_handler.py
# Andres Miguel Escolastico Lara. 23-EISN-2-056

import os
import random
from PIL import Image
import requests
import io
import openai
import re
import json
import shutil
import datetime
import gc
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API de OpenAI
# Obtenemos la API key de la variable de entorno OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dalle_image(scene_text, theme="", output_folder="assets/dalle_images"):
    """
    Genera una imagen utilizando DALL·E 3 basada en el texto de una escena.
    
    Args:
        scene_text (str): Texto de la escena
        theme (str): Tema general de la historia para enriquecer el prompt
        output_folder (str): Carpeta donde se guardarán las imágenes generadas
    
    Returns:
        str: Ruta de la imagen generada o None si falla la generación
    """
    try:
        # Asegurarse de que la carpeta de salida existe
        os.makedirs(output_folder, exist_ok=True)
        
        # Preparar el prompt para DALL·E
        # Limitamos a 250 caracteres para mantener el prompt conciso pero descriptivo
        scene_summary = scene_text[:250].strip()
        
        # Extraer palabras clave para el prompt
        keywords = ' '.join(word for word in scene_summary.replace('.', ' ').replace(',', ' ').split()
                         if len(word) > 4)[:100]  # Solo palabras significativas

        # Construir un prompt más eficiente para DALL·E
        prompt = f"Ilustración detallada de una escena de historia: {scene_summary[:150]}. Tema: {theme}. Estilo: alta calidad, vibrante, cinematográfico. Elementos clave: {keywords}"
        
        print(f"Generando imagen con DALL·E para la escena: {scene_summary[:50]}...")
        
        # Hacer la petición a la API de OpenAI
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Obtener la URL de la imagen generada
        image_url = response.data[0].url
        
        # Descargar la imagen
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Crear un nombre de archivo único basado en un timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dalle_image_{timestamp}.png"
            image_path = os.path.join(output_folder, filename)
            
            # Guardar la imagen en disco
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            print(f"Imagen DALL·E guardada en: {image_path}")
            
            # Liberar memoria
            if 'image_response' in locals():
                del image_response
            gc.collect()  # Forzar recolección de basura después de procesar imágenes grandes
            
            return image_path
        else:
            print(f"Error al descargar imagen: Código de estado {image_response.status_code}")
            return None
    
    except Exception as e:
        print(f"Error al generar imagen con DALL·E: {e}")
        return None

def select_themed_images(scenes, theme, image_folder=None, use_dalle=True):
    """
    Genera imágenes para cada escena usando DALL·E basadas en el texto de la escena y el tema.
    
    Args:
        scenes (list): Lista de descripciones de escenas
        theme (str): Tema general de la historia
        image_folder (str): No utilizado, mantenido por compatibilidad
        use_dalle (bool): No utilizado, mantenido por compatibilidad (siempre generará con DALL·E)
    
    Returns:
        list: Lista de rutas de imágenes generadas
    """
    # Crear carpeta para imágenes DALL·E
    os.makedirs("assets/dalle_images", exist_ok=True)
    
    generated_images = []
    
    # Generar una imagen con DALL·E para cada escena
    for scene in scenes:
        # Generar imagen con DALL·E
        dalle_image = generate_dalle_image(scene, theme)
        
        if dalle_image:
            # Si se generó correctamente, añadirla a la lista
            generated_images.append(dalle_image)
        else:
            # Si falló, usar una imagen de placeholder
            print(f"Error al generar imagen para escena: {scene[:30]}...")
            # Crear una imagen de placeholder simple con PIL
            placeholder_img = Image.new('RGB', (512, 512), color=(200, 200, 200))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            placeholder_path = os.path.join("assets/dalle_images", f"placeholder_{timestamp}.png")
            placeholder_img.save(placeholder_path)
            generated_images.append(placeholder_path)
    
    # Liberar memoria después de procesar todas las imágenes
    gc.collect()
    
    return generated_images

def generate_scene_descriptions(scenes):
    """
    Genera descripciones cortas para las imágenes basadas en las escenas.
    
    Args:
        scenes (list): Lista de textos de escenas
    
    Returns:
        list: Lista de descripciones para imágenes
    """
    descriptions = []
    
    for scene in scenes:
        # Limitamos a los primeros 200 caracteres para mantener la descripción concisa
        short_desc = scene[:200].strip()
        # Añadimos la descripción a la lista
        descriptions.append(short_desc)
    
    return descriptions

# Mantenemos estas funciones por compatibilidad con el código existente
# pero ya no se utilizarán para seleccionar imágenes

def organize_images(source_folder="assets/images", organized_folder="assets/organized_images"):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    print("Función organize_images() está deshabilitada. Se usarán imágenes de DALL·E.")
    return {"total": 0, "categories": {}, "mapping": {}}

def select_local_images(scenes, image_folder="assets/images"):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    print("Función select_local_images() está deshabilitada. Se usarán imágenes de DALL·E.")
    return select_themed_images(scenes, "")

def select_relevant_image(scene_text, image_folder="assets/organized_images"):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    print("Función select_relevant_image() está deshabilitada. Se usarán imágenes de DALL·E.")
    return None

def analyze_scene_for_keywords(scene_text):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    return {"categories": [], "subcategories": []}

def rename_image(old_path, new_name, dest_folder=None):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    print("Función rename_image() está deshabilitada.")
    return None

def batch_rename_images(naming_convention, source_folder="assets/images", dest_folder=None):
    """Función mantenida por compatibilidad, pero ya no se utiliza"""
    print("Función batch_rename_images() está deshabilitada.")
    return {}