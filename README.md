# Proyecto-de-Final-IA

## Nombre

Andres Miguel Escolastico Lara 

## Matrícula

23-EISN-2-056

## Proyecto

# Generador de Historias Interactivas

## Descripción
Este proyecto es un generador de historias interactivas que utiliza inteligencia artificial para crear experiencias narrativas completas. La aplicación combina modelos avanzados de lenguaje para generar historias coherentes, sintetiza voz para narrarlas, y utiliza DALL·E 3 para crear imágenes únicas que ilustran cada escena. Todo esto se reproduce de manera sincronizada con música de fondo para crear una experiencia inmersiva.

## Características principales
- **Generación de historias**: Utiliza OpenAI GPT-3.5-Turbo para crear narrativas coherentes y estructuradas a partir de cualquier tema proporcionado por el usuario.
- **Imágenes generadas con IA**: Implementa DALL·E 3 para crear ilustraciones visuales únicas para cada escena de la historia.
- **Narración por voz**: Convierte el texto de la historia a voz utilizando síntesis de voz para una experiencia auditiva.
- **Música de fondo**: Reproduce música ambiental que complementa la narración.
- **Cambio automático de escenas**: Las imágenes cambian automáticamente siguiendo el ritmo de la narración.
- **Interfaz intuitiva**: Diseñada con Streamlit para una experiencia de usuario sencilla y agradable.

## Tecnologías utilizadas
- **Python 3.8+**: Lenguaje principal del proyecto
- **Streamlit**: Framework para la interfaz gráfica de usuario
- **OpenAI API**: 
  - GPT-3.5-Turbo para generar historias
  - DALL·E 3 para crear imágenes
- **pyttsx3**: Biblioteca para síntesis de voz
- **Pygame**: Manejo de la reproducción de audio
- **Pillow (PIL)**: Procesamiento de imágenes
- **python-dotenv**: Gestión de variables de entorno

## Estructura del proyecto
```
├── app.py                  # Aplicación principal de Streamlit
├── story_generator.py      # Generación de historias usando OpenAI
├── image_handler.py        # Generación de imágenes con DALL·E
├── text_to_speech.py       # Conversión de texto a voz
├── audio_handler.py        # Manejo de reproducción de audio
├── utils.py                # Utilidades y funciones auxiliares
├── .env                    # Variables de entorno (no incluido en el repositorio)
├── .env.example            # Ejemplo de configuración de variables de entorno
├── requirements.txt        # Dependencias del proyecto
├── assets/                 # Carpeta para almacenar recursos
│   ├── music/              # Música de fondo
│   ├── images/             # Imágenes originales (no utilizadas actualmente)
│   └── dalle_images/       # Imágenes generadas por DALL·E
└── output/                 # Carpeta para guardar historias generadas
```

## Instalación

### Requisitos previos
- Python 3.8 o superior
- Cuenta de OpenAI con API key (para GPT-3.5-Turbo y DALL·E 3)

### Pasos para la instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/am399315/Proyecto-Final-IA.git
   cd generador-historias-interactivas
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura tus variables de entorno:
   - Copia el archivo `.env.example` a `.env`
   - Añade tu API key de OpenAI en el archivo `.env`:
     ```
     OPENAI_API_KEY=tu_clave_api_de_openai_aqui
     ```

4. Prepara las carpetas para los recursos:
   ```bash
   mkdir -p assets/music assets/dalle_images output
   ```

5. (Opcional) Añade archivos de música de fondo en la carpeta `assets/music` en formato MP3 o WAV.

## Uso

1. Inicia la aplicación:
   ```bash
   streamlit run app.py
   ```

2. Ingresa un tema para tu historia en el campo de texto.

3. Haz clic en "Generar Historia" y espera mientras:
   - Se genera la historia basada en el tema
   - Se crean imágenes para cada escena con DALL·E
   - Se convierte el texto a voz
   - Se selecciona música de fondo

4. Una vez generada la historia, puedes:
   - Hacer clic en "▶️ Reproducir" para iniciar la narración
   - Usar "⏹️ Detener" para parar la reproducción
   - Pulsar "⏭️ Siguiente" para avanzar manualmente a la siguiente escena

## Flujo de trabajo interno

1. **Generación de la historia**:
   - El usuario proporciona un tema
   - GPT-3.5-Turbo genera una historia estructurada en escenas

2. **Creación de imágenes**:
   - Para cada escena, se genera un prompt para DALL·E 3
   - DALL·E crea imágenes que representan visualmente cada escena

3. **Síntesis de voz**:
   - El texto completo de la historia se convierte a voz
   - Se calculan los tiempos aproximados para cada escena

4. **Reproducción sincronizada**:
   - La narración de voz comienza a reproducirse
   - Un sistema de temporización cambia automáticamente las imágenes
   - La música de fondo acompaña la narración

## Personalización

- **Música**: Añade tus propios archivos de música en la carpeta `assets/music`
- **Voz**: Modifica la velocidad y el tipo de voz en `text_to_speech.py`
- **Prompts**: Ajusta los prompts para GPT y DALL·E en `story_generator.py` e `image_handler.py`

## Notas importantes

- Se requiere una conexión a internet para la generación de historias e imágenes
- La API de OpenAI tiene costos asociados según el uso
- El proyecto utiliza archivos temporales para almacenar audio e imágenes generadas

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir:
1. Haz un fork del repositorio
2. Crea una rama para tu función (`git checkout -b feature/nueva-funcion`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva función'`)
4. Haz push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request



## Contacto

[Andres Miguel Escolastico Lara] - [am399315@gmail.com]

Enlace del proyecto: [https://github.com/am399315/Proyecto-Final-IA.git](https://github.com/am399315/Proyecto-Final-IA.git)

# Andres Miguel Escolastico Lara. 23-EISN-2-056
