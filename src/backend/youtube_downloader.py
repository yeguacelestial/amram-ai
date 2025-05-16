"""
Módulo para descargar videos de YouTube utilizando yt-dlp.
"""
import os
import logging
from typing import Dict, Optional, Tuple
import yt_dlp

from ..utils.config import DOWNLOADS_DIR, MAX_AUDIO_QUALITY

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """
    Clase para gestionar la descarga de audio desde videos de YouTube.
    """
    def __init__(self, output_dir: str = DOWNLOADS_DIR):
        """
        Inicializa el downloader con un directorio de salida.
        
        Args:
            output_dir: Directorio donde se guardarán los archivos descargados.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Opciones base para yt-dlp
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'verbose': False,
        }
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Obtiene información básica del video sin descargarlo.
        
        Args:
            url: URL del video de YouTube.
            
        Returns:
            Diccionario con información del video o None si hay un error.
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'upload_date': info.get('upload_date')
                }
        except Exception as e:
            logger.error(f"Error al obtener información del video: {e}")
            return None
    
    def download_audio(self, url: str, progress_callback=None) -> Tuple[bool, Optional[str]]:
        """
        Descarga el audio de un video de YouTube.
        
        Args:
            url: URL del video de YouTube.
            progress_callback: Función opcional para reportar el progreso.
            
        Returns:
            Tupla con (éxito, ruta_del_archivo) o (False, None) si hay un error.
        """
        try:
            # Si tenemos un callback de progreso, configuramos un hook de progreso
            if progress_callback:
                class ProgressHook:
                    def __call__(self, d):
                        if d['status'] == 'downloading':
                            if 'total_bytes' in d and 'downloaded_bytes' in d:
                                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                                progress_callback(percent)
                            elif 'total_bytes_estimate' in d:
                                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                                progress_callback(percent)
                
                self.ydl_opts['progress_hooks'] = [ProgressHook()]
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # yt-dlp maneja la extracción de audio automáticamente con los postprocessors
                
                # Determinar la ruta del archivo descargado
                filename = ydl.prepare_filename(info)
                # Cambiar la extensión a wav (porque nuestro postprocessor lo convierte)
                filepath = os.path.splitext(filename)[0] + '.wav'
                
                if os.path.exists(filepath):
                    logger.info(f"Descarga completada: {filepath}")
                    return True, filepath
                else:
                    logger.error(f"El archivo descargado no se encuentra: {filepath}")
                    return False, None
                
        except Exception as e:
            logger.error(f"Error al descargar audio: {e}")
            return False, None


# Ejemplo de uso
if __name__ == "__main__":
    # Este código solo se ejecuta si el script es ejecutado directamente
    downloader = YouTubeDownloader()
    
    # URL de ejemplo
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Obtener información del video
    video_info = downloader.get_video_info(test_url)
    if video_info:
        print(f"Título: {video_info['title']}")
        print(f"Duración: {video_info['duration']} segundos")
    
    # Descargar el audio
    def progress(percent):
        print(f"Descarga: {percent:.1f}%")
    
    success, file_path = downloader.download_audio(test_url, progress)
    if success:
        print(f"Archivo descargado: {file_path}")
    else:
        print("Error al descargar el audio")
