"""
Módulo para procesar audio y separar pistas utilizando modelos de AI.
"""
import os
import logging
import tempfile
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import torch
from datetime import datetime, timedelta

from ..utils.config import (
    PROCESSED_DIR, 
    SAMPLE_RATE, 
    DEMUCS_MODEL, 
    DEMUCS_SEGMENT, 
    DEMUCS_OVERLAP,
    MODELS_DIR
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Clase para manejar el procesamiento de audio y la separación de pistas.
    """
    def __init__(self, output_dir: str = PROCESSED_DIR, model_name: str = DEMUCS_MODEL):
        """
        Inicializa el procesador de audio.
        
        Args:
            output_dir: Directorio donde se guardarán los archivos procesados.
            model_name: Nombre del modelo de Demucs a utilizar.
        """
        self.output_dir = Path(output_dir)
        self.model_name = model_name
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Mapa de caché de modelos para evitar recargar modelos
        self._model_cache = {}
        
        # Demucs debe ser importado después de importar torch
        try:
            import torch
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            from demucs.audio import AudioFile, save_audio
            from demucs.states import load_model
            
            # Detectar hardware disponible y configurar opciones de optimización
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Utilizando dispositivo: {self.device}")
            
            # Configurar opciones de rendimiento según el dispositivo
            if self.device == "cuda":
                # Configurar para GPU 
                torch.backends.cudnn.benchmark = True
                logger.info("Optimización CUDNN activada para mejorar rendimiento")
            else:
                # Configurar para CPU - usar múltiples núcleos cuando sea posible
                torch.set_num_threads(os.cpu_count())
                logger.info(f"Usando {torch.get_num_threads()} hilos para procesamiento en CPU")
            
            # Asegurar que el directorio de modelos exista
            os.makedirs(MODELS_DIR, exist_ok=True)
            
            # Intentar cargar el modelo
            try:
                # Cargar modelo y guardar en caché
                self.model = self._load_model(self.model_name)
                logger.info(f"Modelo {self.model_name} cargado correctamente.")
                self._demucs_available = True
            except Exception as e:
                logger.warning(f"Error al cargar el modelo {self.model_name}: {e}")
                logger.info("Se utilizará un modelo alternativo (htdemucs) si está disponible.")
                try:
                    self.model_name = "htdemucs"
                    self.model = self._load_model(self.model_name)
                    logger.info(f"Modelo alternativo {self.model_name} cargado correctamente.")
                    self._demucs_available = True
                except Exception as e:
                    logger.error(f"Error al cargar modelo alternativo: {e}")
                    self._demucs_available = False
            
        except ImportError as e:
            logger.warning(f"Demucs no está instalado correctamente: {e}")
            logger.warning("La separación de pistas no estará disponible.")
            self._demucs_available = False
    
    def _load_model(self, model_name: str):
        """
        Cargar modelo de Demucs con caché.
        
        Args:
            model_name: Nombre del modelo a cargar.
            
        Returns:
            Modelo cargado.
        """
        from demucs.pretrained import get_model
        
        # Verificar si el modelo ya está en caché
        if model_name in self._model_cache:
            logger.info(f"Usando modelo {model_name} desde caché")
            return self._model_cache[model_name]
        
        # Cargar el modelo y guardarlo en caché
        logger.info(f"Cargando modelo {model_name}...")
        start_time = time.time()
        model = get_model(model_name)
        model.to(self.device)
        load_time = time.time() - start_time
        logger.info(f"Modelo {model_name} cargado en {load_time:.2f} segundos")
        
        # Guardar en caché
        self._model_cache[model_name] = model
        return model
    
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        Carga un archivo de audio y lo convierte a la tasa de muestreo estándar.
        
        Args:
            audio_path: Ruta al archivo de audio.
            
        Returns:
            Tupla con el array numpy del audio y la tasa de muestreo.
        """
        logger.info(f"Cargando audio: {audio_path}")
        start_time = time.time()
        
        try:
            # Intentar cargar con librosa
            audio, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=False)
            
            # Si el audio es mono, convertirlo a estéreo (2 canales)
            if audio.ndim == 1:
                audio = np.stack([audio, audio])
            
            load_time = time.time() - start_time
            logger.info(f"Audio cargado: {audio.shape}, SR={sr}, Duración: {audio.shape[1]/sr:.2f}s, Tiempo de carga: {load_time:.2f}s")
            return audio, sr
        except Exception as e:
            logger.error(f"Error al cargar audio con librosa: {e}")
            raise
    
    def separate_tracks(self, audio_path: str, progress_callback=None) -> Optional[Dict[str, str]]:
        """
        Separa un archivo de audio en pistas individuales utilizando Demucs.
        
        Args:
            audio_path: Ruta al archivo de audio.
            progress_callback: Función opcional para reportar el progreso.
            
        Returns:
            Diccionario con los nombres de las pistas y las rutas a los archivos separados,
            o None si hay un error.
        """
        if not self._demucs_available:
            logger.warning("Demucs no está disponible. La separación de pistas es simulada.")
            # En la versión de prueba de concepto, simularemos la separación
            return self._simulate_track_separation(audio_path, progress_callback)
        
        total_start_time = time.time()
        logger.info(f"Iniciando separación de pistas: {audio_path}")
        
        try:
            # Importamos estas funciones aquí para asegurarnos de que demucs esté instalado
            from demucs.audio import AudioFile, save_audio
            from demucs.apply import apply_model
            
            # Generar nombre de salida basado en el nombre del archivo original
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_dir = self.output_dir / audio_name
            os.makedirs(output_dir, exist_ok=True)
            
            # Cargar audio con la función de Demucs
            logger.info(f"[1/4] Cargando y preparando audio...")
            load_start = time.time()
            
            wav = AudioFile(audio_path).read(streams=0, samplerate=SAMPLE_RATE, channels=2)
            ref = wav.mean(0)
            wav = (wav - ref.mean()) / ref.std()
            
            # Convertir a tensor de PyTorch (corregido para evitar advertencia)
            # El resultado de AudioFile.read() ya es un tensor, no necesitamos convertirlo
            wav_tensor = wav.float()  # Aseguramos que sea float
            
            load_time = time.time() - load_start
            logger.info(f"Audio cargado y normalizado. Forma: {wav_tensor.shape}, Tiempo: {load_time:.2f}s")
            
            # Optimizar tamaño de segmento según memoria disponible
            if self.device == "cuda":
                # Usar segmentos más grandes en GPU
                seg_length = min(int(DEMUCS_SEGMENT * SAMPLE_RATE), wav_tensor.shape[1])
            else:
                # Usar segmentos más pequeños en CPU para mejor rendimiento
                # pero no tan pequeños que afecten la calidad
                optimal_segment = min(DEMUCS_SEGMENT, 6.0)  # 6 segundos máximo en CPU
                seg_length = min(int(optimal_segment * SAMPLE_RATE), wav_tensor.shape[1])
            
            overlap_length = int(DEMUCS_OVERLAP * SAMPLE_RATE)
            
            # Estimar duración total
            audio_duration = wav_tensor.shape[1] / SAMPLE_RATE
            logger.info(f"Duración del audio: {audio_duration:.2f} segundos")
            
            # Estimar tiempo de procesamiento
            est_process_seconds_per_second = 1.5 if self.device == "cuda" else 8.0  # Estimado: GPU=1.5x, CPU=8x
            est_total_seconds = audio_duration * est_process_seconds_per_second
            est_completion_time = datetime.now() + timedelta(seconds=est_total_seconds)
            
            logger.info(f"Tiempo estimado de procesamiento: {est_total_seconds:.1f} segundos")
            logger.info(f"Hora estimada de finalización: {est_completion_time.strftime('%H:%M:%S')}")
            
            # Calcular número de segmentos para mostrar progreso
            padded_length = wav_tensor.shape[1] + 2 * overlap_length
            num_segments = max(1, int(np.ceil(padded_length / (seg_length - overlap_length))))
            
            logger.info(f"[2/4] Separando pistas, usando {num_segments} segmentos de {seg_length/SAMPLE_RATE:.1f}s...")
            separation_start = time.time()
            
            # Separar las fuentes por chunks para manejar audios largos
            sources = self._separate_chunks(wav_tensor, progress_callback, num_segments, seg_length, overlap_length)
            
            if sources is None:
                logger.error("Error durante la separación por chunks. No se pudieron obtener fuentes.")
                return None
                
            separation_time = time.time() - separation_start
            logger.info(f"Separación completada en {separation_time:.2f}s. Guardando pistas...")
            
            # Guardar cada pista separada
            logger.info("[3/4] Guardando pistas separadas...")
            save_start = time.time()
            
            track_paths = {}
            sources_list = list(self.model.sources)
            
            # Calculamos la cantidad de sources para actualizar el progreso
            total_sources = len(sources_list)
            
            # Verificar integridad de las fuentes separadas
            if sources.shape[0] != len(sources_list):
                logger.warning(f"Advertencia: Número de fuentes no coincide. Esperado: {len(sources_list)}, Obtenido: {sources.shape[0]}")
                # Ajustar la lista de fuentes si es necesario
                if sources.shape[0] < len(sources_list):
                    sources_list = sources_list[:sources.shape[0]]
                    logger.warning(f"Ajustando lista de fuentes a: {sources_list}")
                
            # Progreso de exportación: desde 80% hasta 100%
            export_progress_base = 80
            export_progress_step = 20 / total_sources if total_sources > 0 else 0
            
            for i, source_name in enumerate(sources_list):
                try:
                    logger.info(f"Guardando pista {i+1}/{total_sources}: {source_name}")
                    
                    # Verificar índice válido
                    if i >= sources.shape[0]:
                        logger.error(f"Índice de fuente fuera de rango: {i} >= {sources.shape[0]}")
                        continue
                        
                    source_audio = sources[i].cpu().numpy()
                    
                    # Restaurar la escala original
                    source_audio = source_audio * ref.std() + ref.mean()
                    
                    # Ruta de salida
                    output_path = output_dir / f"{source_name}.wav"
                    
                    # Guardar el audio
                    sf.write(str(output_path), source_audio.T, SAMPLE_RATE)
                    
                    track_paths[source_name] = str(output_path)
                    
                    # Actualizar progreso final (separación completa)
                    if progress_callback:
                        # Progreso: 80% -> 100% durante exportación
                        progress = export_progress_base + ((i + 1) * export_progress_step)
                        progress_callback(min(progress, 100))  # Asegurar que no supere 100%
                    
                    logger.info(f"Pista {source_name} guardada: {output_path}")
                    
                except Exception as e:
                    logger.error(f"Error al guardar pista {source_name}: {e}")
                    # Continuar con la siguiente pista
            
            # Verificar si se guardaron todas las pistas esperadas
            if len(track_paths) < total_sources:
                logger.warning(f"No se guardaron todas las pistas. Esperadas: {total_sources}, Guardadas: {len(track_paths)}")
            
            save_time = time.time() - save_start
            logger.info(f"Guardadas {len(track_paths)} pistas en {save_time:.2f}s")
            
            # Limpiar memoria
            logger.info("[4/4] Limpiando memoria...")
            del sources, wav_tensor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            total_time = time.time() - total_start_time
            logger.info(f"Proceso completo finalizado en {total_time:.2f}s")
            
            return track_paths
            
        except Exception as e:
            logger.error(f"Error al separar pistas: {e}", exc_info=True)
            return None
    
    def _separate_chunks(self, wav_tensor, progress_callback=None, num_segments=1, 
                         seg_length=None, overlap_length=None):
        """
        Separa el audio en chunks para manejar archivos grandes.
        
        Args:
            wav_tensor: Tensor de PyTorch con el audio a separar.
            progress_callback: Función para reportar progreso.
            num_segments: Número estimado de segmentos.
            seg_length: Longitud del segmento en muestras.
            overlap_length: Longitud del solapamiento en muestras.
            
        Returns:
            Tensor con las fuentes separadas.
        """
        import torch
        from demucs.apply import apply_model
        
        # Configurar parámetros de segmentación
        if seg_length is None:
            seg_length = int(DEMUCS_SEGMENT * SAMPLE_RATE)
        if overlap_length is None:
            overlap_length = int(DEMUCS_OVERLAP * SAMPLE_RATE)
        
        # Si el audio es más corto que el segmento, procesarlo directamente
        if wav_tensor.shape[1] <= seg_length:
            logger.info("Audio más corto que el segmento, procesando directamente.")
            start_time = time.time()
            if progress_callback:
                progress_callback(10)  # Indicamos 10% de progreso inicial
            
            # Añadir dimensión de batch
            wav_batch = wav_tensor.unsqueeze(0).to(self.device)
            
            # Aplicar el modelo
            with torch.no_grad():
                sources = apply_model(self.model, wav_batch, device=self.device)
            
            process_time = time.time() - start_time
            logger.info(f"Procesamiento directo completado en {process_time:.2f}s")
            
            if progress_callback:
                progress_callback(80)  # Indicamos 80% de progreso
                
            # Quitar dimensión de batch
            return sources.squeeze(0)
        
        # Para audios largos, procesar por chunks
        total_length = wav_tensor.shape[1]
        # Calcular el número real de segmentos necesarios con solapamiento
        real_segment_stride = seg_length - overlap_length
        actual_num_segments = int(np.ceil((total_length - overlap_length) / real_segment_stride))
        
        logger.info(f"Procesando audio por chunks: {actual_num_segments} segmentos reales " +
                   f"(estimados: {num_segments}) de {seg_length/SAMPLE_RATE:.2f}s " +
                   f"con solapamiento de {overlap_length/SAMPLE_RATE:.2f}s")
        
        # Primero procesamos un segmento pequeño para obtener la forma del resultado
        # Esto nos permite crear el tensor de salida con las dimensiones correctas
        with torch.no_grad():
            # Extraer un segmento corto
            logger.info("Procesando segmento de prueba para determinar dimensiones...")
            sample_start = time.time()
            
            segment = wav_tensor[:, :min(seg_length, wav_tensor.shape[1])]
            segment_batch = segment.unsqueeze(0).to(self.device)
            
            # Aplicar el modelo al segmento de prueba
            sources = apply_model(self.model, segment_batch, device=self.device)
            
            # Quitar dimensión de batch para obtener forma
            sources = sources.squeeze(0)
            
            sample_time = time.time() - sample_start
            logger.info(f"Segmento de prueba procesado en {sample_time:.2f}s")
            
            # Liberar memoria
            del segment_batch
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        # Obtener dimensiones del resultado
        sources_count, channels, _ = sources.shape
        logger.info(f"Configurando buffer para {sources_count} fuentes, {channels} canales")
        
        # Crear tensor para almacenar todas las fuentes (en CPU para evitar problemas de memoria en GPU)
        logger.info(f"Creando buffer para resultado final de tamaño {sources_count}x{channels}x{total_length}")
        all_sources = torch.zeros(sources_count, channels, total_length, 
                              dtype=torch.float32, device=torch.device("cpu"))
        
        # Procesar el audio por chunks con solapamiento
        segment_start = 0
        segment_count = 0
        last_segment_start = -1  # Para detectar falta de avance
        last_segment_end = 0
        
        # Variables para detección de bucle infinito
        max_segments = min(actual_num_segments * 2, 1000)  # Límite de seguridad contra bucles
        current_progress = 0
        consecutive_no_progress = 0  # Contador de iteraciones sin avance
        max_no_progress = 3  # Máximo permitido de iteraciones sin avance
        
        # Variables para estimación de tiempo
        processing_times = []
        start_timestamp = datetime.now()
        
        logger.info(f"Hora de inicio del procesamiento: {start_timestamp.strftime('%H:%M:%S')}")
        
        while segment_start < total_length and segment_count < max_segments:
            # Timestamp actual para monitoreo
            current_timestamp = datetime.now()
            elapsed = (current_timestamp - start_timestamp).total_seconds()
            
            # Calcular el final del segmento actual
            segment_end = min(segment_start + seg_length, total_length)
            
            # Detección de bucle: si no avanzamos entre iteraciones
            if segment_start == last_segment_start:
                consecutive_no_progress += 1
                logger.warning(f"⚠️ No hay avance en el segmento: {consecutive_no_progress}/{max_no_progress}")
                
                if consecutive_no_progress >= max_no_progress:
                    logger.error(f"❌ Bucle infinito detectado. Forzando avance significativo.")
                    # Avanzar a la mitad del audio o por un gran segmento
                    segment_start = min(segment_start + seg_length * 2, total_length)
                    segment_end = min(segment_start + seg_length, total_length)
                    consecutive_no_progress = 0  # Reiniciar contador
                    
                    # Si aún estamos al final o muy cerca, terminar el procesamiento
                    if segment_start >= total_length - seg_length // 4:
                        logger.warning("Llegando al final del audio. Terminando procesamiento.")
                        break
            else:
                consecutive_no_progress = 0  # Reiniciar contador si hubo avance
            
            # Guardar posición actual para la próxima iteración
            last_segment_start = segment_start
            last_segment_end = segment_end
            
            chunk_start_time = time.time()
            
            # Extraer el segmento actual
            logger.info(f"Procesando segmento {segment_count+1}/{actual_num_segments}: " +
                       f"{segment_start/SAMPLE_RATE:.2f}s - {segment_end/SAMPLE_RATE:.2f}s " +
                       f"[{elapsed:.1f}s transcurridos]")
            
            segment = wav_tensor[:, segment_start:segment_end]
            
            # Verificar que el segmento tenga longitud positiva
            if segment.shape[1] <= 0:
                logger.warning("Segmento con longitud 0 o negativa. Avanzando al siguiente.")
                segment_start = min(segment_start + real_segment_stride, total_length)
                continue
            
            # Añadir dimensión de batch
            segment_batch = segment.unsqueeze(0).to(self.device)
            
            # Aplicar el modelo al segmento actual
            with torch.no_grad():
                try:
                    sources = apply_model(self.model, segment_batch, device=self.device)
                    # Quitar dimensión de batch
                    sources = sources.squeeze(0)
                except Exception as e:
                    logger.error(f"Error al procesar segmento {segment_count+1}: {e}")
                    # Avanzar al siguiente segmento, intentando saltar la región problemática
                    segment_start = min(segment_start + real_segment_stride, total_length)
                    continue
            
            # Calcular regiones de solapamiento
            # En el primer segmento, no hay solapamiento al inicio
            overlap_start = 0 if segment_start == 0 else overlap_length
            # En el último segmento, no hay solapamiento al final
            overlap_end = 0 if segment_end == total_length else overlap_length
            
            # Región efectiva del segmento actual
            effective_start = segment_start + overlap_start
            effective_end = segment_end - overlap_end
            
            # Comprobar si la región efectiva tiene tamaño positivo
            if effective_end <= effective_start:
                logger.warning(f"Región efectiva inválida: {effective_start}-{effective_end}. Avanzando.")
                segment_start = min(segment_start + real_segment_stride, total_length)
                continue
            
            # Copiar la región efectiva a la salida final
            # Asegurar que los índices no superen los límites del tensor
            effective_length = min(segment.shape[1] - overlap_start - overlap_end, 
                                  effective_end - effective_start)
                                  
            if effective_length > 0:
                try:
                    # Verificar que los índices estén dentro de los límites
                    all_sources[:, :, effective_start:effective_end] = sources[:, :, 
                                                                       overlap_start:overlap_start+effective_length]
                except Exception as e:
                    logger.error(f"Error al copiar región efectiva: {e}")
                    logger.error(f"Dimensiones - Fuentes: {sources.shape}, Región: {overlap_start}:{overlap_start+effective_length}, "
                              f"Destino: {effective_start}:{effective_end}")
                    # Continuar con el siguiente segmento
            else:
                logger.warning("Longitud efectiva <= 0, saltando copia de datos")
            
            # Avanzar al siguiente segmento de manera consistente
            next_start = segment_start + real_segment_stride
            
            # Si el avance es muy pequeño o nulo, forzar un avance mínimo
            if next_start <= segment_start:
                next_start = segment_start + max(1, seg_length // 4)
                logger.warning(f"Avance insuficiente. Forzando avance a {next_start/SAMPLE_RATE:.2f}s")
            
            segment_start = min(next_start, total_length)
            
            # Calcular tiempo de procesamiento y estimar tiempo restante
            chunk_time = time.time() - chunk_start_time
            processing_times.append(chunk_time)
            
            # Mantener solo los últimos 5 tiempos para una mejor estimación adaptativa
            if len(processing_times) > 5:
                processing_times = processing_times[-5:]
                
            avg_chunk_time = sum(processing_times) / len(processing_times)
            
            # Calcular progreso real basado en la posición actual
            progress_ratio = min(segment_start / total_length, 1.0)
            segments_left = actual_num_segments - (segment_count + 1)
            segments_left = max(0, segments_left)  # Asegurar que no sea negativo
            est_remaining_time = segments_left * avg_chunk_time
            
            # Calcular tiempo estimado de finalización
            eta = current_timestamp + timedelta(seconds=est_remaining_time)
            
            logger.info(f"Segmento {segment_count+1}/{actual_num_segments} procesado en {chunk_time:.2f}s. "
                      f"Progreso: {progress_ratio*100:.1f}%. "
                      f"Tiempo restante: {est_remaining_time:.2f}s. "
                      f"ETA: {eta.strftime('%H:%M:%S')}")
            
            segment_count += 1
            
            # Actualizar progreso (La separación ocupa el 0-80% del progreso total)
            if progress_callback:
                # Calcular progreso basado en la posición actual, no en el conteo de segmentos
                new_progress = min(progress_ratio * 80, 80)
                
                # Solo actualizar si hay un cambio significativo (evitar actualizaciones constantes)
                if abs(new_progress - current_progress) >= 1:
                    current_progress = new_progress
                    progress_callback(current_progress)
            
            # Liberar memoria
            del segment_batch, sources
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        # Verificar si el procesamiento fue interrumpido por límite de segmentos
        if segment_count >= max_segments and segment_start < total_length:
            logger.warning(f"Se alcanzó el límite de segmentos ({max_segments}). Procesamiento incompleto.")
        
        end_timestamp = datetime.now()
        total_processing_time = (end_timestamp - start_timestamp).total_seconds()
        
        logger.info(f"Procesados {segment_count} segmentos en {total_processing_time:.2f}s")
        logger.info(f"Hora de finalización: {end_timestamp.strftime('%H:%M:%S')}")
        
        return all_sources
    
    def _simulate_track_separation(self, audio_path: str, progress_callback=None) -> Dict[str, str]:
        """
        Simula la separación de pistas para la prueba de concepto.
        
        Args:
            audio_path: Ruta al archivo de audio original.
            progress_callback: Función para reportar progreso.
            
        Returns:
            Diccionario con nombres de pistas y rutas simuladas.
        """
        logger.info(f"Iniciando separación simulada para: {audio_path}")
        start_time = time.time()
        
        audio, sr = self.load_audio(audio_path)
        
        # Generar nombres de salida
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_dir = self.output_dir / audio_name
        os.makedirs(output_dir, exist_ok=True)
        
        # Diferentes instrumentos que Demucs puede separar
        instruments = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other']
        track_paths = {}
        
        # Simular progreso
        total_steps = len(instruments)
        
        for i, instrument in enumerate(instruments):
            # Simular tiempo de procesamiento
            process_time = 0.5  # Simular medio segundo para cada instrumento
            time.sleep(process_time)
            
            logger.info(f"Simulando separación de {instrument} ({i+1}/{total_steps})")
            
            # En la versión simulada, simplemente creamos copias del audio original
            # con diferentes niveles para simular diferentes instrumentos
            
            # Factores de volumen artificial para simular diferentes instrumentos
            volume_factors = {
                'vocals': 0.8,
                'drums': 0.6,
                'bass': 0.7,
                'guitar': 0.5,
                'piano': 0.4,
                'other': 0.3
            }
            
            # Crear una copia modificada del audio para simular la pista separada
            track_audio = audio * volume_factors.get(instrument, 0.5)
            
            # Ruta de salida
            output_path = output_dir / f"{instrument}.wav"
            
            # Guardar el audio
            sf.write(str(output_path), track_audio.T, sr)
            
            track_paths[instrument] = str(output_path)
            
            # Actualizar progreso
            if progress_callback:
                progress_callback(((i + 1) / total_steps) * 100)
            
            logger.info(f"Pista simulada guardada: {output_path}")
        
        total_time = time.time() - start_time
        logger.info(f"Separación simulada completada en {total_time:.2f}s")
        
        return track_paths
    
    def mix_tracks(self, tracks: Dict[str, Tuple[str, float]], output_path: str) -> bool:
        """
        Mezcla varias pistas con diferentes niveles de volumen.
        
        Args:
            tracks: Diccionario con nombres de pistas, rutas y niveles (0.0-1.0).
            output_path: Ruta del archivo de salida.
            
        Returns:
            True si la mezcla fue exitosa, False en caso contrario.
        """
        try:
            logger.info(f"Mezclando {len(tracks)} pistas...")
            start_time = time.time()
            
            # Cargar todas las pistas
            loaded_tracks = {}
            sr = None
            length = None
            
            for name, (track_path, level) in tracks.items():
                if os.path.exists(track_path):
                    logger.info(f"Cargando pista {name} con nivel {level}")
                    audio, track_sr = self.load_audio(track_path)
                    
                    if sr is None:
                        sr = track_sr
                    
                    # Ajustar volumen
                    audio = audio * level
                    
                    loaded_tracks[name] = audio
                    
                    # Guardar la longitud de la pista más corta
                    if length is None or audio.shape[1] < length:
                        length = audio.shape[1]
            
            if not loaded_tracks:
                logger.error("No se pudo cargar ninguna pista para mezclar")
                return False
            
            logger.info(f"Mezclando pistas con longitud {length} muestras ({length/sr:.2f}s)")
            
            # Mezclar pistas recortadas a la misma longitud
            mix = None
            for name, audio in loaded_tracks.items():
                if mix is None:
                    mix = audio[:, :length]
                else:
                    mix += audio[:, :length]
            
            # Normalizar para evitar clipping
            max_val = np.max(np.abs(mix))
            if max_val > 0:
                mix = mix / max_val * 0.9  # 90% del máximo para evitar distorsión
            
            # Guardar mezcla
            logger.info(f"Guardando mezcla final en {output_path}")
            sf.write(output_path, mix.T, sr)
            
            total_time = time.time() - start_time
            logger.info(f"Mezcla completada y guardada en {total_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al mezclar pistas: {e}")
            return False
    
    def change_model(self, model_name: str) -> bool:
        """
        Cambia el modelo de Demucs a utilizar.
        
        Args:
            model_name: Nombre del modelo a utilizar.
            
        Returns:
            True si el cambio fue exitoso, False en caso contrario.
        """
        if not self._demucs_available:
            logger.warning("Demucs no está disponible, no se puede cambiar el modelo.")
            return False
        
        try:
            # Intentar cargar el nuevo modelo usando caché
            logger.info(f"Cambiando al modelo: {model_name}")
            start_time = time.time()
            
            # Cargar modelo (desde caché si está disponible)
            self.model = self._load_model(model_name)
            self.model_name = model_name
            
            change_time = time.time() - start_time
            logger.info(f"Modelo cambiado a {model_name} en {change_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error al cambiar el modelo a {model_name}: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Obtiene la lista de modelos disponibles en Demucs.
        
        Returns:
            Lista de nombres de modelos disponibles.
        """
        if not self._demucs_available:
            logger.warning("Demucs no está disponible, no se pueden listar los modelos.")
            return []
        
        try:
            from demucs.pretrained import PRETRAINED_MODELS
            models = list(PRETRAINED_MODELS.keys())
            logger.info(f"Modelos disponibles: {len(models)}")
            return models
        except Exception as e:
            logger.error(f"Error al obtener modelos disponibles: {e}")
            return []
    
    def get_hardware_info(self) -> Dict[str, str]:
        """
        Obtiene información sobre el hardware disponible.
        
        Returns:
            Diccionario con información del hardware.
        """
        info = {
            "dispositivo": self.device,
            "torch_version": torch.__version__,
            "num_threads": str(torch.get_num_threads()),
        }
        
        if self.device == "cuda":
            info["cuda_version"] = torch.version.cuda
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB"
        else:
            import multiprocessing
            info["cpu_cores"] = str(multiprocessing.cpu_count())
        
        return info


# Ejemplo de uso
if __name__ == "__main__":
    # Este código solo se ejecuta si el script es ejecutado directamente
    processor = AudioProcessor()
    
    # Ejemplo de progreso
    def progress(percent):
        print(f"\rProgreso: {percent:.1f}%", end="")
    
    # Mostrar información de hardware
    hardware_info = processor.get_hardware_info()
    print("\nInformación de hardware:")
    for key, value in hardware_info.items():
        print(f"- {key}: {value}")
    
    # Ruta de ejemplo (ajustar según necesidades)
    audio_file = "/ruta/a/tu/archivo.mp3"
    if os.path.exists(audio_file):
        tracks = processor.separate_tracks(audio_file, progress)
        if tracks:
            print("\nPistas separadas:")
            for instrument, path in tracks.items():
                print(f"- {instrument}: {path}")
    else:
        print(f"El archivo {audio_file} no existe.")
