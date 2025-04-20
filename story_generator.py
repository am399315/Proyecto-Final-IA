# story_generator.py
# Andres Miguel Escolastico Lara. 23-EISN-2-056

import os
import openai
import json
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar la API key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Caché para historias generadas
_story_cache = {}

def generate_story(theme, max_length=1000, num_scenes=5, temperature=0.7, retry_attempts=2):
    """
    Genera una historia basada en un tema proporcionado usando GPT-4o-mini.
    
    Args:
        theme (str): El tema de la historia
        max_length (int): Longitud máxima de la historia en tokens
        num_scenes (int): Número aproximado de escenas a generar
        temperature (float): Temperatura para la generación (mayor = más creativo)
        retry_attempts (int): Número de intentos en caso de error
    
    Returns:
        dict: Un diccionario con la historia y las escenas para imágenes
    """
    # Verificar caché para evitar regenerar la misma historia
    cache_key = f"{theme}_{max_length}_{num_scenes}_{temperature}"
    if cache_key in _story_cache:
        print("Recuperando historia de caché")
        return _story_cache[cache_key]
    
    # Si no está en caché, generarla
    attempts = 0
    
    while attempts <= retry_attempts:
        try:
            # Prompt optimizado para GPT-4o-mini
            prompt = f"""
            Crea una historia interesante y original sobre el tema: '{theme}'.
            La historia debe seguir esta estructura:
            1. Una introducción que presente los personajes y el escenario
            2. Desarrollo de la trama con aproximadamente {num_scenes} escenas principales
            3. Una conclusión o resolución satisfactoria
            
            Para cada escena importante, inserta el marcador [NUEVA_ESCENA] y asegúrate de que la escena siguiente tenga una descripción visual clara.
            Limita la historia a aproximadamente {num_scenes} escenas principales.
            Incluye descripciones vívidas que permitan al lector visualizar cada escena.
            """
            
            # Llamada a la API de OpenAI con exponential backoff
            # Cambiado de "gpt-3.5-turbo" a "gpt-4o-mini"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un narrador creativo que crea historias inmersivas y visuales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            # Obtener la respuesta
            story_text = response.choices[0].message.content.strip()
            
            # Verificar que la historia sea adecuada (tenga al menos 2 escenas)
            scenes = story_text.split("[NUEVA_ESCENA]")
            if len(scenes) < 2:
                # Agregar marcadores de escena si no los hay
                scenes = story_text.split("\n\n")
                story_text = "[NUEVA_ESCENA]".join(scenes)
                scenes = story_text.split("[NUEVA_ESCENA]")
            
            # Eliminar escenas vacías
            scenes = [scene.strip() for scene in scenes if scene.strip()]
            
            # Crear un diccionario con la historia completa y las escenas
            story_data = {
                "full_story": story_text.replace("[NUEVA_ESCENA]", ""),
                "scenes": scenes
            }
            
            # Guardar en caché para futuros usos
            _story_cache[cache_key] = story_data
            
            return story_data
        
        except Exception as e:
            attempts += 1
            print(f"Intento {attempts} fallido: {e}")
            
            if attempts <= retry_attempts:
                # Esperar con backoff exponencial
                wait_time = 2 ** attempts
                print(f"Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                print(f"Error al generar la historia después de {attempts} intentos: {e}")
                return {"full_story": "Lo siento, hubo un error al generar la historia.", "scenes": []}