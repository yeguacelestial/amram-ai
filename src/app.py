"""
Aplicación principal para Amram AI.
Prueba de concepto para la primera fase del proyecto.
"""
import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
import curses
import glob

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurar que podemos importar los módulos de nuestro proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import DOWNLOADS_DIR, PROCESSED_DIR, AUDIO_EXTENSIONS
from src.backend.youtube_downloader import YouTubeDownloader
from src.backend.audio_processor import AudioProcessor

def print_banner():
    """Muestra un banner en la consola."""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║                  AMRAM AI                         ║
    ║        Separación de pistas de audio              ║
    ║          Prueba de Concepto v0.2                  ║
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
    
    # Agregar tiempo actual para monitorear que el proceso sigue vivo
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Si estamos en la fase de separación y entre 75-85%, agregar nota
    if prefix == "Separación" and 75 <= percent <= 85:
        print(f"\r[{current_time}] {prefix}: |{bar}| {percent:.1f}% - Finalizando procesamiento y exportando pistas...", end='')
    else:
        print(f"\r[{current_time}] {prefix}: |{bar}| {percent:.1f}%", end='')
    
    if percent == 100:
        print()

def file_selector(initial_dir=None):
    """
    Muestra un selector de archivos navegable con flechas del teclado.
    
    Args:
        initial_dir: Directorio inicial para comenzar la navegación.
        
    Returns:
        Ruta del archivo seleccionado o None si se canceló.
    """
    # Normalizar el directorio inicial
    if initial_dir is None:
        initial_dir = os.path.expanduser("~")
    current_dir = os.path.abspath(initial_dir)
    
    # Iniciar curses
    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Para directorios
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Para archivos de audio
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Para selección
    
    try:
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        selected_option = 0
        scroll_offset = 0
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Obtener lista de directorios y archivos
            try:
                items = []
                
                # Agregar opción para subir un nivel (..)
                if os.path.dirname(current_dir) != current_dir:
                    items.append(("..", "dir"))
                
                # Listar directorios y archivos
                dirs = sorted([d for d in os.listdir(current_dir) 
                              if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.')])
                
                # Filtrar archivos de audio por extensiones
                audio_files = []
                for ext in AUDIO_EXTENSIONS:
                    audio_files.extend(glob.glob(os.path.join(current_dir, f"*{ext}")))
                audio_files = sorted([os.path.basename(f) for f in audio_files])
                
                # Añadir directorios y archivos de audio a la lista
                for d in dirs:
                    items.append((d, "dir"))
                for f in audio_files:
                    items.append((f, "audio"))
                
                # Ajustar selección si el directorio cambió y hay menos items
                if selected_option >= len(items):
                    selected_option = len(items) - 1 if len(items) > 0 else 0
                
                # Ajustar desplazamiento
                if selected_option < scroll_offset:
                    scroll_offset = selected_option
                if selected_option >= scroll_offset + (height - 4):
                    scroll_offset = selected_option - (height - 5)
                
                # Mostrar directorio actual
                title = f"Seleccione un archivo de audio en: {current_dir}"
                stdscr.addstr(0, 0, title[:width-1])
                stdscr.addstr(1, 0, "="*min(len(title), width-1))
                
                # Mostrar instrucciones
                footer = "↑↓: Navegar | →: Entrar | ←: Subir | Enter: Seleccionar | Esc: Cancelar"
                stdscr.addstr(height-1, 0, footer[:width-1])
                
                # Mostrar items
                display_lines = height - 4  # Espacio disponible para items
                for i in range(min(display_lines, len(items))):
                    idx = i + scroll_offset
                    if idx < len(items):
                        name, item_type = items[idx]
                        
                        # Estilo según tipo
                        if idx == selected_option:
                            attr = curses.color_pair(3)  # Seleccionado
                        elif item_type == "dir":
                            attr = curses.color_pair(1)  # Directorio
                        elif item_type == "audio":
                            attr = curses.color_pair(2)  # Audio
                        else:
                            attr = 0  # Normal
                        
                        # Preparar texto a mostrar
                        if item_type == "dir":
                            display_text = f"📁 {name}/"
                        else:
                            display_text = f"🎵 {name}"
                        
                        # Truncar si es necesario
                        if len(display_text) > width - 3:
                            display_text = display_text[:width-6] + "..."
                        
                        stdscr.addstr(i+2, 0, display_text, attr)
                
            except Exception as e:
                # Mostrar error
                stdscr.addstr(2, 0, f"Error al leer directorio: {str(e)[:width-30]}")
                current_dir = os.path.dirname(current_dir)  # Subir un nivel
            
            # Refrescar pantalla
            stdscr.refresh()
            
            # Obtener entrada del usuario
            key = stdscr.getch()
            
            if key == curses.KEY_UP and selected_option > 0:
                selected_option -= 1
            elif key == curses.KEY_DOWN and selected_option < len(items) - 1:
                selected_option += 1
            elif key == curses.KEY_RIGHT and selected_option < len(items):
                # Entrar en directorio
                name, item_type = items[selected_option]
                if item_type == "dir":
                    if name == "..":
                        current_dir = os.path.dirname(current_dir)
                    else:
                        new_dir = os.path.join(current_dir, name)
                        if os.path.isdir(new_dir):
                            current_dir = new_dir
                    selected_option = 0
                    scroll_offset = 0
            elif key == curses.KEY_LEFT:
                # Subir un nivel
                if os.path.dirname(current_dir) != current_dir:
                    current_dir = os.path.dirname(current_dir)
                    selected_option = 0
                    scroll_offset = 0
            elif key == 10:  # Enter
                # Seleccionar archivo o entrar en directorio
                if len(items) > 0:
                    name, item_type = items[selected_option]
                    if item_type == "dir":
                        if name == "..":
                            current_dir = os.path.dirname(current_dir)
                        else:
                            new_dir = os.path.join(current_dir, name)
                            if os.path.isdir(new_dir):
                                current_dir = new_dir
                        selected_option = 0
                        scroll_offset = 0
                    elif item_type == "audio":
                        # Devolver la ruta completa del archivo seleccionado
                        return os.path.join(current_dir, name)
            elif key == 27:  # Escape
                # Cancelar selección
                return None
            
    finally:
        # Restaurar terminal
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
    return None

def main():
    """Función principal de la aplicación."""
    print_banner()
    
    # Verificar directorios necesarios
    for directory in [DOWNLOADS_DIR, PROCESSED_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Inicializar componentes
    downloader = YouTubeDownloader()
    processor = AudioProcessor()
    
    # Mostrar información detallada sobre el hardware
    print("\n========== INFORMACIÓN DEL SISTEMA ==========")
    hardware_info = processor.get_hardware_info()
    device_type = "GPU" if hardware_info.get("dispositivo") == "cuda" else "CPU"
    
    print(f"• Dispositivo: {device_type}")
    
    if device_type == "GPU":
        print(f"• GPU: {hardware_info.get('gpu_name', 'Desconocido')}")
        print(f"• Memoria GPU: {hardware_info.get('gpu_memory', 'Desconocido')}")
    else:
        print(f"• Núcleos CPU: {hardware_info.get('cpu_cores', 'Desconocido')}")
        print(f"• Hilos en uso: {hardware_info.get('num_threads', 'Desconocido')}")
    
    print(f"• Versión PyTorch: {hardware_info.get('torch_version', 'Desconocido')}")
    
    # Si el modelo de Demucs está disponible, mostrar información
    if hasattr(processor, '_demucs_available') and processor._demucs_available:
        print(f"\n• Modelo Demucs: {processor.model_name}")
        print("• Estado: Activo - Separación real disponible")
    else:
        print("\n• Estado Demucs: Inactivo - Se usará separación simulada")
        print("  NOTA: Instale Demucs correctamente para usar separación real")
    
    print("==============================================")
    
    # Flujo de la aplicación
    while True:
        print("\n" + "="*50)
        print("OPCIONES PRINCIPALES:")
        print("1. Descargar audio de YouTube")
        print("2. Procesar archivo de audio local")
        print("3. Cambiar modelo de separación")
        print("4. Salir")
        
        choice = input("\nSeleccione una opción (1-4): ")
        
        if choice == '1':
            # Descargar de YouTube
            url = input("\nIngrese URL de YouTube: ")
            
            # Obtener información del video
            print("\nObteniendo información del video...")
            video_info = downloader.get_video_info(url)
            if not video_info:
                print("❌ No se pudo obtener información del video. Verifique la URL.")
                continue
            
            print(f"\n✅ Video encontrado:")
            print(f"• Título: {video_info['title']}")
            print(f"• Duración: {video_info['duration']} segundos ({video_info['duration']/60:.1f} minutos)")
            
            confirm = input("\n¿Desea descargar este video? (s/n): ").lower()
            if confirm != 's':
                continue
            
            print("\nDescargando audio...")
            download_start = time.time()
            
            def download_progress(percent):
                progress_callback(percent, "Descarga")
                
            success, audio_path = downloader.download_audio(url, download_progress)
            
            if not success:
                print("\n❌ Error al descargar el audio.")
                continue
            
            download_time = time.time() - download_start
            print(f"\n✅ Audio descargado en {download_time:.2f} segundos: {audio_path}")
            
            # Preguntar si desea procesar el audio
            process = input("\n¿Desea separar las pistas de este audio? (s/n): ").lower()
            if process != 's':
                continue
            
            process_audio(audio_path, processor)
            
        elif choice == '2':
            # Procesar archivo local con navegador de archivos
            print("\nAbriendo selector de archivos...")
            audio_path = file_selector(DOWNLOADS_DIR)
            
            if audio_path is None:
                print("❌ Selección de archivo cancelada.")
                continue
                
            if not os.path.exists(audio_path):
                print(f"❌ El archivo {audio_path} no existe.")
                continue
            
            process_audio(audio_path, processor)
            
        elif choice == '3':
            # Cambiar modelo de separación
            if not hasattr(processor, '_demucs_available') or not processor._demucs_available:
                print("\n❌ Demucs no está disponible. No se puede cambiar el modelo.")
                continue
            
            # Obtener modelos disponibles
            print("\nObteniendo lista de modelos disponibles...")
            available_models = processor.get_available_models()
            
            if not available_models:
                print("\n❌ No se pudo obtener la lista de modelos disponibles.")
                continue
            
            print("\n📋 Modelos disponibles:")
            for i, model in enumerate(available_models, 1):
                # Mostrar asterisco junto al modelo actual
                current = " ★" if model == processor.model_name else ""
                print(f"{i}. {model}{current}")
            
            print("\nRecomendaciones:")
            print("• htdemucs: Mejor equilibrio calidad/rendimiento (predeterminado)")
            print("• htdemucs_ft: Mejor calidad, más lento (4x más procesamiento)")
            print("• mdx: Buen rendimiento para la mayoría de los casos")
            print("• mdx_q: Versión cuantizada (más rápida pero menos precisa)")
            
            try:
                model_idx = int(input("\nSeleccione un modelo (número): ")) - 1
                if 0 <= model_idx < len(available_models):
                    selected_model = available_models[model_idx]
                    
                    if selected_model == processor.model_name:
                        print(f"\nℹ️ El modelo {selected_model} ya está activo.")
                        continue
                    
                    print(f"\nCambiando al modelo: {selected_model}...")
                    change_start = time.time()
                    
                    if processor.change_model(selected_model):
                        change_time = time.time() - change_start
                        print(f"✅ Modelo cambiado exitosamente a {selected_model} en {change_time:.2f} segundos.")
                    else:
                        print(f"❌ Error al cambiar al modelo {selected_model}.")
                else:
                    print("❌ Número de modelo inválido.")
            except ValueError:
                print("❌ Por favor ingrese un número válido.")
            
        elif choice == '4':
            # Salir
            print("\n👋 ¡Gracias por usar Amram AI!")
            break
            
        else:
            print("\n❌ Opción no válida. Intente nuevamente.")

def process_audio(audio_path, processor):
    """
    Procesa un archivo de audio para separar las pistas.
    
    Args:
        audio_path: Ruta al archivo de audio.
        processor: Instancia de AudioProcessor.
    """
    print("\n🔊 Iniciando separación de pistas...")
    print("📄 Archivo: " + os.path.basename(audio_path))
    process_start = time.time()
    
    # Mostrar detalles del procesamiento
    print("\n⚙️ Configuración:")
    print(f"• Modelo: {processor.model_name}")
    print(f"• Dispositivo: {processor.device.upper()}")
    
    # Cargar el audio para obtener información
    try:
        audio, sr = processor.load_audio(audio_path)
        duration = audio.shape[1] / sr
        print(f"• Duración: {duration:.2f} segundos ({duration/60:.2f} minutos)")
        print(f"• Canales: {audio.shape[0]}")
        print(f"• Tasa de muestreo: {sr} Hz")
        
        # Estimar tiempo de procesamiento
        est_process_seconds_per_second = 1.5 if processor.device == "cuda" else 8.0
        est_total_seconds = duration * est_process_seconds_per_second
        est_completion_time = datetime.now() + timedelta(seconds=est_total_seconds)
        
        print(f"• Tiempo estimado: ~{est_total_seconds:.1f} segundos ({est_total_seconds/60:.1f} minutos)")
        print(f"• Finalización estimada: {est_completion_time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"• Error al analizar audio: {e}")
    
    if processor.device == "cuda":
        print("• Aceleración GPU activa")
        # Mostrar información de memoria GPU si está disponible
        hardware_info = processor.get_hardware_info()
        if "gpu_memory" in hardware_info:
            print(f"• Memoria GPU: {hardware_info['gpu_memory']}")
    
    # Recordatorio para el usuario
    print("\n💡 El proceso puede tardar varios minutos dependiendo del tamaño del archivo.")
    print("   Se mostrarán actualizaciones de progreso durante el proceso...")
    print("   Si la barra de progreso se detiene en ~80%, significa que está exportando las pistas separadas")
    
    def separation_progress(percent):
        progress_callback(percent, "Separación")
    
    # Ejecutar separación de pistas
    print("\n⏱️ Inicio: " + datetime.now().strftime("%H:%M:%S"))
    tracks = processor.separate_tracks(audio_path, separation_progress)
    
    if not tracks:
        print("\n❌ Error al separar las pistas.")
        return
    
    process_time = time.time() - process_start
    print(f"\n✅ Separación completada en {process_time:.2f} segundos ({process_time/60:.2f} minutos)")
    
    # Mostrar información de pistas separadas
    print(f"\n🎵 Pistas separadas ({len(tracks)}):")
    for instrument, path in tracks.items():
        filename = os.path.basename(path)
        print(f"• {instrument}: {filename}")
        print(f"  Ubicación: {path}")
    
    # Crear una mezcla personalizada
    print("\n🎚️ Creando una mezcla personalizada...")
    print("Ajuste los niveles de volumen para cada pista:")
    
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
                    print("❌ El nivel debe estar entre 0.0 y 1.0")
            except ValueError:
                print("❌ Por favor ingrese un número válido")
    
    # Generar nombre para la mezcla personalizada
    audio_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_mix = os.path.join(PROCESSED_DIR, f"{audio_name}_mezcla_personalizada.wav")
    
    print("\nCreando mezcla final...")
    mix_start = time.time()
    
    if processor.mix_tracks(mix_tracks, output_mix):
        mix_time = time.time() - mix_start
        print(f"\n✅ Mezcla guardada en: {output_mix}")
        print(f"   Tiempo de procesamiento: {mix_time:.2f} segundos")
    else:
        print("\n❌ Error al crear la mezcla personalizada.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Programa interrumpido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"\n❌ Error inesperado: {e}") 