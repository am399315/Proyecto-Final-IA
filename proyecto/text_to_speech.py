# text_to_speech.py
# Andres Miguel Escolastico Lara. 23-EISN-2-056

import os
import pyttsx3
import tempfile
import re
import threading

# Cache para el motor de texto a voz
_tts_engine = None

def get_tts_engine():
    """
    Obtiene una instancia del motor de texto a voz.
    Reutiliza la instancia si ya existe para mejorar el rendimiento.
    
    Returns:
        pyttsx3.Engine: Instancia del motor de texto a voz
    """
    global _tts_engine
    
    if _tts_engine is None:
        # Inicializar el motor de texto a voz
        _tts_engine = pyttsx3.init()
        
        # Configurar propiedades de voz
        voices = _tts_engine.getProperty('voices')
        # Seleccionar una voz en español si está disponible
        for voice in voices:
            if 'spanish' in voice.name.lower():
                _tts_engine.setProperty('voice', voice.id)
                break
        
        # Ajustar la velocidad (valores más bajos = más lento)
        _tts_engine.setProperty('rate', 150)
    
    return _tts_engine

def clean_text_for_tts(text):
    """
    Limpia y optimiza el texto para la conversión a voz.
    
    Args:
        text (str): Texto a limpiar
    
    Returns:
        str: Texto limpio optimizado para TTS
    """
    # Eliminar caracteres especiales que pueden causar problemas en TTS
    text = re.sub(r'[^\w\s.,;:¿?¡!""()\-—–]', ' ', text)
    
    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Asegurar pausas en puntuación
    text = text.replace('.', '. ')
    text = text.replace('!', '! ')
    text = text.replace('?', '? ')
    text = text.replace(';', '; ')
    
    return text.strip()

def text_to_speech(text, output_file=None):
    """
    Convierte texto a voz y lo guarda como un archivo de audio.
    
    Args:
        text (str): El texto a convertir a voz
        output_file (str, optional): Ruta del archivo de salida. Si es None, se crea un archivo temporal.
    
    Returns:
        str: Ruta del archivo de audio generado
    """
    try:
        # Limpiar el texto para optimizar la conversión
        cleaned_text = clean_text_for_tts(text)
        
        # Obtener el motor TTS reutilizable
        engine = get_tts_engine()
        
        # Crear un archivo temporal si no se proporciona uno
        if output_file is None:
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, 'story_narration.wav')  # Cambiado a .wav para mejor compatibilidad
        
        # Asegurarse de que la extensión sea .wav
        if not output_file.lower().endswith('.wav'):
            base_name = os.path.splitext(output_file)[0]
            output_file = f"{base_name}.wav"
        
        # Generar el archivo de audio
        engine.save_to_file(cleaned_text, output_file)
        engine.runAndWait()
        
        return output_file
    
    except Exception as e:
        print(f"Error en la conversión de texto a voz: {e}")
        return None

def narrate_by_scenes(scenes, output_dir=None):
    """
    Genera archivos de audio para cada escena de la historia.
    
    Args:
        scenes (list): Lista de textos de escenas
        output_dir (str, optional): Directorio para guardar los archivos. Si es None, se usan archivos temporales.
    
    Returns:
        list: Lista de rutas de archivos de audio generados
    """
    audio_files = []
    
    for i, scene in enumerate(scenes):
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"scene_{i+1}.wav")  # Cambiado a .wav
        else:
            output_file = None
        
        audio_file = text_to_speech(scene, output_file)
        if audio_file:
            audio_files.append(audio_file)
    
    return audio_files