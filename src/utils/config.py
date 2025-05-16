"""
Archivo de configuración para Amram AI.
Contiene rutas de directorios y parámetros de configuración.
"""
import os
from pathlib import Path

# Directorios principales
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = PROJECT_ROOT / "data"
TEMP_DIR = DATA_DIR / "temp"
DOWNLOADS_DIR = DATA_DIR / "downloads"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

# Crear directorios si no existen
for dir_path in [DATA_DIR, TEMP_DIR, DOWNLOADS_DIR, PROCESSED_DIR, MODELS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Parámetros de audio
SAMPLE_RATE = 44100
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']

# Parámetros del modelo de separación (Demucs)
DEMUCS_MODEL = "htdemucs"  # Modelo de Demucs a utilizar
DEMUCS_SEGMENT = 10  # Tamaño del segmento en segundos
DEMUCS_OVERLAP = 0.1  # Solapamiento entre segmentos

# Parámetros de YouTube
MAX_AUDIO_QUALITY = "best"  # Calidad máxima para descargar audio de YouTube

# Configuración de la interfaz (futuro)
DEFAULT_THEME = "dark"
