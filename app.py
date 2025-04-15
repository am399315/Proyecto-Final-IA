# app.py
# Andres Miguel Escolastico Lara.  23-EISN-2-056

import streamlit as st
import os
import time
import pygame
from PIL import Image
import io
import threading

# Importar módulos personalizados
from story_generator import generate_story
from text_to_speech import text_to_speech, narrate_by_scenes
from image_handler import generate_scene_descriptions, select_themed_images
from audio_handler import select_background_music, initialize_pygame_mixer, play_background_music, play_narration, stop_background_music, stop_all_audio, check_scene_queue
from utils import create_project_folders, save_story_data, estimate_narration_time

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Generador de Historias Interactivas",
    page_icon="📚",
    layout="wide"
)

# Inicializar pygame para la reproducción de audio
initialize_pygame_mixer()

# Crear las carpetas necesarias para el proyecto
create_project_folders()

# Crear carpeta para imágenes DALL·E
os.makedirs("assets/dalle_images", exist_ok=True)

# Variables de estado para la narración
if 'story_playing' not in st.session_state:
    st.session_state.story_playing = False
if 'current_scene' not in st.session_state:
    st.session_state.current_scene = 0
if 'story_data' not in st.session_state:
    st.session_state.story_data = None
if 'image_paths' not in st.session_state:
    st.session_state.image_paths = []
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'music_file' not in st.session_state:
    st.session_state.music_file = None
if 'scene_times' not in st.session_state:
    st.session_state.scene_times = []
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
if 'change_counter' not in st.session_state:
    st.session_state.change_counter = 0
# Variable para forzar actualizaciones de UI
if 'force_update' not in st.session_state:
    st.session_state.force_update = 0
# Archivo temporal para comunicación entre sesiones
scene_state_file = ".streamlit_scene_state.txt"

def update_scene_state_file(scene_index):
    """
    Actualiza el archivo de estado con la escena actual para garantizar
    la sincronización entre diferentes sesiones de Streamlit.
    """
    try:
        with open(scene_state_file, "w") as f:
            f.write(f"{scene_index},{time.time()}")
    except Exception as e:
        print(f"Error al escribir archivo de estado: {e}")

def read_scene_state_file():
    """
    Lee el archivo de estado para obtener la última escena seleccionada.
    """
    try:
        if os.path.exists(scene_state_file):
            with open(scene_state_file, "r") as f:
                data = f.read().strip()
                if data:
                    scene, timestamp = data.split(",")
                    return int(scene), float(timestamp)
    except Exception as e:
        print(f"Error al leer archivo de estado: {e}")
    return None, None

def manual_scene_change():
    """Función para cambiar manualmente a la siguiente escena (para botones)"""
    if not st.session_state.story_playing:
        return
    
    if st.session_state.current_scene < len(st.session_state.scene_times) - 1:
        st.session_state.current_scene += 1
        st.session_state.change_counter += 1
        st.session_state.force_update += 1
        update_scene_state_file(st.session_state.current_scene)
        st.rerun()
    else:
        stop_playback()

def start_playback():
    """Inicia la reproducción de la historia"""
    if not st.session_state.story_data or not st.session_state.image_paths:
        st.error("No hay historia para reproducir.")
        return
    
    # Calcular los tiempos para cada escena
    st.session_state.scene_times = [
        estimate_narration_time(scene) for scene in st.session_state.story_data["scenes"]
    ]
    
    # Iniciar la reproducción
    st.session_state.story_playing = True
    st.session_state.current_scene = 0
    st.session_state.last_update_time = time.time()
    st.session_state.change_counter += 1
    st.session_state.force_update += 1
    update_scene_state_file(0)  # Iniciar en escena 0
    
    # Iniciar la música de fondo (utiliza el canal 1)
    if st.session_state.music_file and os.path.exists(st.session_state.music_file):
        play_background_music(st.session_state.music_file, volume=0.3)
    
    # Reproducir la narración (utiliza el canal 0)
    if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
        try:
            # Usar la función play_narration con los tiempos de escena
            play_narration(
                st.session_state.audio_file, 
                volume=0.7,
                scene_times=st.session_state.scene_times
            )
        except Exception as e:
            st.error(f"Error al reproducir la narración: {e}")
    
    st.rerun()

def stop_playback():
    """Detiene la reproducción de la historia"""
    st.session_state.story_playing = False
    st.session_state.current_scene = 0
    st.session_state.change_counter += 1
    st.session_state.force_update += 1
    update_scene_state_file(0)  # Reiniciar a escena 0
    stop_all_audio()  # Detiene tanto la música de fondo como la narración
    st.rerun()

def check_scene_progress():
    """Comprueba si es hora de avanzar a la siguiente escena"""
    if not st.session_state.story_playing:
        return False
    
    # 1. Verificar cambios en el archivo de estado (alta prioridad)
    file_scene, file_timestamp = read_scene_state_file()
    if (file_scene is not None and 
        file_scene != st.session_state.current_scene and 
        file_timestamp > st.session_state.last_update_time):
        # El archivo de estado indica un cambio de escena más reciente
        print(f"Actualizando escena desde archivo: {file_scene}")
        st.session_state.current_scene = file_scene
        st.session_state.last_update_time = file_timestamp
        st.session_state.force_update += 1
        return True
    
    # 2. Verificar si hay solicitudes de cambio de escena en la cola
    new_scene = check_scene_queue()
    if new_scene is not None and new_scene > 0:
        # Actualizar la escena actual
        if new_scene < len(st.session_state.scene_times):
            print(f"Actualizando escena desde cola: {new_scene}")
            st.session_state.current_scene = new_scene
            st.session_state.last_update_time = time.time()
            st.session_state.force_update += 1
            update_scene_state_file(new_scene)
            return True
    
    # 3. Método original basado en tiempo como respaldo
    if st.session_state.last_update_time is not None:
        current_time = time.time()
        elapsed_time = current_time - st.session_state.last_update_time
        
        # Si estamos en la última escena y ha pasado su tiempo, terminar
        if st.session_state.current_scene >= len(st.session_state.scene_times) - 1:
            if elapsed_time >= st.session_state.scene_times[st.session_state.current_scene]:
                stop_playback()
                return True
        
        # Comprobar si es hora de avanzar a la siguiente escena
        if elapsed_time >= st.session_state.scene_times[st.session_state.current_scene]:
            # Avanzar a la siguiente escena
            new_scene_index = st.session_state.current_scene + 1
            print(f"Avanzando a escena por tiempo: {new_scene_index}")
            st.session_state.current_scene = new_scene_index
            st.session_state.last_update_time = current_time
            st.session_state.force_update += 1
            update_scene_state_file(new_scene_index)
            return True
    
    return False

# Título de la aplicación
st.title("📚 Generador de Historias Interactivas con DALL·E")
st.markdown("---")

# Sección de entrada del tema
st.header("Ingresa el tema de tu historia")
theme = st.text_input("Tema de la historia:", placeholder="Por ejemplo: Un viaje espacial, Un tesoro perdido, etc.")

# Botón de generación
generate_button = st.button("Generar Historia", type="primary")

# Sección de visualización y reproducción
st.markdown("---")
col1, col2 = st.columns([2, 3])

with col1:
    st.header("Control de Reproducción")
    
    # Botones de control
    play_col, stop_col, next_col = st.columns(3)
    with play_col:
        if st.button("▶️ Reproducir", disabled=st.session_state.story_playing or not st.session_state.story_data):
            start_playback()
    
    with stop_col:
        if st.button("⏹️ Detener", disabled=not st.session_state.story_playing):
            stop_playback()
    
    with next_col:
        if st.button("⏭️ Siguiente", disabled=not st.session_state.story_playing):
            manual_scene_change()
    
    # Mostrar la historia completa
    if st.session_state.story_data:
        st.subheader("Historia Completa")
        st.write(st.session_state.story_data["full_story"])

with col2:
    st.header("Visualización")
    
    # Valor invisible para forzar actualizaciones
    st.empty().markdown(f"<!-- Forzar actualización: {st.session_state.force_update} -->")
    
    # Mostrar número de escena actual y total (para seguimiento)
    if st.session_state.story_data and len(st.session_state.story_data["scenes"]) > 0:
        st.caption(f"Escena {st.session_state.current_scene + 1} de {len(st.session_state.story_data['scenes'])}")
    
    # Mostrar la imagen actual
    image_container = st.container()
    with image_container:
        if st.session_state.image_paths and len(st.session_state.image_paths) > 0:
            if 0 <= st.session_state.current_scene < len(st.session_state.image_paths):
                current_image_path = st.session_state.image_paths[st.session_state.current_scene]
                if os.path.exists(current_image_path):
                    img = Image.open(current_image_path)
                    st.image(img, caption=f"Escena {st.session_state.current_scene + 1}", use_container_width=True)
        else:
            st.info("Aquí se mostrarán las imágenes generadas con DALL·E.")
    
    # Mostrar la escena actual (texto)
    if st.session_state.story_data and st.session_state.story_playing:
        if 0 <= st.session_state.current_scene < len(st.session_state.story_data["scenes"]):
            current_scene_text = st.session_state.story_data["scenes"][st.session_state.current_scene]
            st.text_area("Texto de la escena actual:", value=current_scene_text, height=150, disabled=True)

# Generación de la historia
if generate_button and theme:
    with st.spinner("Generando historia e imágenes con DALL·E... Esto puede tardar unos momentos."):
        try:
            # Generar la historia
            story_data = generate_story(theme)
            
            if not story_data or not story_data["scenes"]:
                st.error("No se pudo generar la historia. Por favor, intenta con otro tema.")
            else:
                # Guardar la historia generada
                st.session_state.story_data = story_data
                
                # Seleccionar imágenes para las escenas
                scene_descriptions = generate_scene_descriptions(story_data["scenes"])
                
                # Generar imágenes con DALL·E para cada escena
                image_paths = select_themed_images(scene_descriptions, theme)
                st.session_state.image_paths = image_paths
                
                # Seleccionar música de fondo
                music_file = select_background_music()
                st.session_state.music_file = music_file
                
                # Generar narración
                audio_file = text_to_speech(story_data["full_story"])
                st.session_state.audio_file = audio_file
                
                # Guardar los datos en un archivo
                save_story_data(story_data, theme)
                
                st.success("¡Historia e imágenes generadas con éxito! Puedes reproducirla ahora.")
                st.rerun()
        except Exception as e:
            st.error(f"Error al generar la historia: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# Comprobar si es necesario avanzar a la siguiente escena
if st.session_state.story_playing:
    scene_changed = check_scene_progress()
    if scene_changed:
        st.rerun()
    else:
        # Usar un placeholder con menor impacto que rerun completo
        refresh_placeholder = st.empty()
        refresh_placeholder.markdown(f"<!-- Actualizando: {time.time()} -->")
        time.sleep(0.3)  # Aumentar ligeramente para reducir la frecuencia de actualización
        st.rerun()