# audio_handler.py
# Andres Miguel Escolastico Lara. 23-EISN-2-056

import os
import random
import pygame
import time
import threading
import queue

def select_background_music(mood="neutral", music_folder="assets/music"):
    """
    Selecciona música de fondo según el estado de ánimo de la historia.
    
    Args:
        mood (str): El estado de ánimo de la historia (happy, sad, suspense, neutral)
        music_folder (str): Carpeta donde se encuentran los archivos de música
    
    Returns:
        str: Ruta del archivo de música seleccionado o None si no hay archivos disponibles
    """
    # Asegurarse de que la carpeta de música existe
    os.makedirs(music_folder, exist_ok=True)
    
    # Obtener una lista de archivos de música disponibles
    music_files = [f for f in os.listdir(music_folder) 
                  if f.lower().endswith(('.mp3', '.wav'))]
    
    # Si no hay archivos de música, devolver None
    if not music_files:
        print("No se encontraron archivos de música en la carpeta especificada.")
        return None
    
    # Intentar encontrar música que coincida con el estado de ánimo
    matching_files = [f for f in music_files if mood.lower() in f.lower()]
    
    # Si no hay coincidencias, seleccionar un archivo aleatorio
    if matching_files:
        selected_music = random.choice(matching_files)
    else:
        selected_music = random.choice(music_files)
    
    # Devolver la ruta completa
    return os.path.join(music_folder, selected_music)

def initialize_pygame_mixer():
    """
    Inicializa el mezclador de audio de Pygame con soporte para múltiples canales.
    """
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        # Configurar canales para permitir reproducción simultánea
        pygame.mixer.set_num_channels(8)
        return True
    except Exception as e:
        print(f"Error al inicializar el mezclador de audio: {e}")
        return False

def play_background_music(music_file, volume=0.3, loop=True):
    """
    Reproduce música de fondo en un canal separado.
    
    Args:
        music_file (str): Ruta del archivo de música
        volume (float): Volumen de reproducción (0.0 a 1.0)
        loop (bool): Si se debe repetir la música
    
    Returns:
        bool: True si la música comenzó a reproducirse, False en caso contrario
    """
    if not music_file or not os.path.exists(music_file):
        print(f"Archivo de música no encontrado o no especificado")
        return False
    
    try:
        # Asegurarse de que el mezclador está inicializado
        if not pygame.mixer.get_init():
            initialize_pygame_mixer()
        
        # Reservar el canal 1 para la música de fondo
        background_channel = pygame.mixer.Channel(1)
        
        # Cargar la música
        sound = pygame.mixer.Sound(music_file)
        sound.set_volume(volume)
        
        # Reproducir la música
        if loop:
            background_channel.play(sound, loops=-1)  # -1 significa loop infinito
        else:
            background_channel.play(sound)
        
        return True
    
    except Exception as e:
        print(f"Error al reproducir música de fondo: {e}")
        return False

# Cola global para comunicación entre threads
scene_change_queue = queue.Queue()

def play_narration(narration_file, volume=0.7, scene_callback=None, scene_times=None):
    """
    Reproduce la narración en un canal separado.
    
    Args:
        narration_file (str): Ruta del archivo de narración
        volume (float): Volumen de reproducción (0.0 a 1.0)
        scene_callback (function): Función de callback para cambio de escenas (opcional)
        scene_times (list): Lista de tiempos para cada escena en segundos (opcional)
    
    Returns:
        bool: True si la narración comenzó a reproducirse, False en caso contrario
    """
    if not narration_file or not os.path.exists(narration_file):
        print(f"Archivo de narración no encontrado o no especificado")
        return False
    
    try:
        # Asegurarse de que el mezclador está inicializado
        if not pygame.mixer.get_init():
            initialize_pygame_mixer()
        
        # Reservar el canal 0 para la narración
        narration_channel = pygame.mixer.Channel(0)
        
        # Cargar la narración
        sound = pygame.mixer.Sound(narration_file)
        sound.set_volume(volume)
        
        # Reproducir la narración
        narration_channel.play(sound)
        
        # Si se proporcionan tiempos de escena, configurar un hilo para cambiar escenas
        if scene_times and len(scene_times) > 0:
            def scene_timer_thread():
                try:
                    start_time = time.time()
                    current_scene = 0
                    accumulated_time = 0
                    
                    while narration_channel.get_busy() and current_scene < len(scene_times):
                        elapsed_time = time.time() - start_time
                        
                        # Calcular tiempo restante para la próxima escena
                        time_to_next_scene = (accumulated_time + scene_times[current_scene]) - elapsed_time
                        
                        if time_to_next_scene <= 0:
                            # Si ya es tiempo de cambiar, avanzar a la siguiente escena
                            accumulated_time += scene_times[current_scene]
                            current_scene += 1
                            
                            # Poner el evento en la cola
                            scene_change_queue.put(current_scene)
                            print(f"[Thread] Cambiando a escena {current_scene}")
                        else:
                            # Dormir hasta la próxima escena o como máximo 0.5 segundos
                            # para mantener la capacidad de respuesta
                            sleep_time = min(time_to_next_scene, 0.5)
                            time.sleep(sleep_time)
                except Exception as e:
                    print(f"Error en scene_timer_thread: {e}")
            
            # Iniciar el hilo para controlar los tiempos de escena
            timer_thread = threading.Thread(target=scene_timer_thread)
            timer_thread.daemon = True
            timer_thread.start()
        
        return True
    
    except Exception as e:
        print(f"Error al reproducir narración: {e}")
        return False

def check_scene_queue():
    """
    Verifica si hay solicitudes de cambio de escena en la cola.
    
    Returns:
        int or None: Índice de la nueva escena o None si no hay cambios
    """
    try:
        if not scene_change_queue.empty():
            return scene_change_queue.get_nowait()
    except Exception:
        pass
    return None

def stop_background_music():
    """
    Detiene la reproducción de música de fondo.
    """
    try:
        if pygame.mixer.get_init():
            # Detener el canal de música de fondo (canal 1)
            if pygame.mixer.Channel(1).get_busy():
                pygame.mixer.Channel(1).stop()
        return True
    except Exception as e:
        print(f"Error al detener la música de fondo: {e}")
        return False

def stop_all_audio():
    """
    Detiene toda la reproducción de audio.
    """
    try:
        if pygame.mixer.get_init():
            pygame.mixer.stop()  # Detiene todos los canales
        
        # Limpiar la cola de cambios de escena
        while not scene_change_queue.empty():
            scene_change_queue.get_nowait()
            
        return True
    except Exception as e:
        print(f"Error al detener todo el audio: {e}")
        return False