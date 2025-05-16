"""
Aplicación principal para Amram AI.
Prueba de concepto para la primera fase del proyecto.
"""
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurar que podemos importar los módulos de nuestro proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import DOWNLOADS_DIR, PROCESSED_DIR
from src.backend.youtube_downloader import YouTubeDownloader
from src.backend.audio_processor import AudioProcessor

def print_banner():
    """Muestra un banner en la consola."""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║                  AMRAM AI                         ║
    ║        Separación de pistas de audio              ║
    ║          Prueba de Concepto v0.1                  ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)

def progress_callback(percent, prefix="Progreso"):
    """
    Muestra una barra de progreso en la consola.
    
    Args:
        percent: Porcentaje de progreso (0-100).
        prefix: Texto que se muestra antes de la barra.
    """
    bar_length = 30
    filled_length = int(bar_length * percent / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    print(f"\r{prefix}: |{bar}| {percent:.1f}%", end='')
    if percent == 100:
        print()

def main():
    """Función principal de la aplicación."""
    print_banner()
    
    # Verificar directorios necesarios
    for directory in [DOWNLOADS_DIR, PROCESSED_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Inicializar componentes
    downloader = YouTubeDownloader()
    processor = AudioProcessor()
    
    # Flujo de la aplicación
    while True:
        print("\n" + "="*50)
        print("Opciones:")
        print("1. Descargar audio de YouTube")
        print("2. Procesar archivo de audio local")
        print("3. Salir")
        
        choice = input("\nSeleccione una opción (1-3): ")
        
        if choice == '1':
            # Descargar de YouTube
            url = input("\nIngrese URL de YouTube: ")
            
            # Obtener información del video
            video_info = downloader.get_video_info(url)
            if not video_info:
                print("No se pudo obtener información del video. Verifique la URL.")
                continue
            
            print(f"\nTítulo: {video_info['title']}")
            print(f"Duración: {video_info['duration']} segundos")
            
            confirm = input("\n¿Desea descargar este video? (s/n): ").lower()
            if confirm != 's':
                continue
            
            print("\nDescargando audio...")
            
            def download_progress(percent):
                progress_callback(percent, "Descarga")
                
            success, audio_path = downloader.download_audio(url, download_progress)
            
            if not success:
                print("\nError al descargar el audio.")
                continue
            
            print(f"\nAudio descargado: {audio_path}")
            
            # Preguntar si desea procesar el audio
            process = input("\n¿Desea separar las pistas de este audio? (s/n): ").lower()
            if process != 's':
                continue
            
            process_audio(audio_path, processor)
            
        elif choice == '2':
            # Procesar archivo local
            path = input("\nIngrese la ruta al archivo de audio: ")
            if not os.path.exists(path):
                print(f"El archivo {path} no existe.")
                continue
            
            process_audio(path, processor)
            
        elif choice == '3':
            # Salir
            print("\n¡Gracias por usar Amram AI!")
            break
            
        else:
            print("\nOpción no válida. Intente nuevamente.")

def process_audio(audio_path, processor):
    """
    Procesa un archivo de audio para separar las pistas.
    
    Args:
        audio_path: Ruta al archivo de audio.
        processor: Instancia de AudioProcessor.
    """
    print("\nSeparando pistas de audio...")
    
    def separation_progress(percent):
        progress_callback(percent, "Separación")
    
    tracks = processor.separate_tracks(audio_path, separation_progress)
    
    if not tracks:
        print("\nError al separar las pistas.")
        return
    
    print("\nPistas separadas:")
    for instrument, path in tracks.items():
        print(f"- {instrument}: {path}")
    
    # Crear una mezcla personalizada
    print("\nCreando una mezcla personalizada...")
    
    # Obtener niveles de volumen para cada pista
    mix_tracks = {}
    for instrument, path in tracks.items():
        while True:
            try:
                level_str = input(f"Nivel para {instrument} (0.0-1.0, 0=silencio, 1=volumen completo): ")
                level = float(level_str)
                if 0 <= level <= 1:
                    mix_tracks[instrument] = (path, level)
                    break
                else:
                    print("El nivel debe estar entre 0.0 y 1.0")
            except ValueError:
                print("Por favor ingrese un número válido")
    
    # Generar nombre para la mezcla personalizada
    audio_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_mix = os.path.join(PROCESSED_DIR, f"{audio_name}_mezcla_personalizada.wav")
    
    if processor.mix_tracks(mix_tracks, output_mix):
        print(f"\nMezcla guardada en: {output_mix}")
    else:
        print("\nError al crear la mezcla personalizada.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"\nError inesperado: {e}") 