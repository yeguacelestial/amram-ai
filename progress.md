# Progreso de desarrollo de Amram AI

Este documento registra el progreso de desarrollo de Amram AI, una aplicación para separar pistas de audio mediante IA local.

## Sesión de trabajo (15/05/2025)

### Configuración del entorno

- [x] Crear entorno conda para el proyecto
  ```bash
  conda create -n amram-ai python=3.10
  conda activate amram-ai
  ```
- [x] Instalar dependencias principales desde conda-forge
  ```bash
  conda install -c conda-forge pytorch torchaudio librosa yt-dlp pyyaml
  ```
- [x] Instalar dependencias adicionales para procesamiento de audio
  ```bash
  pip install soundfile
  ```

### Estructura del proyecto

- [x] Crear estructura de carpetas para el proyecto
  ```
  amram-ai/
  ├── data/
  │   ├── downloads/    # Archivos descargados de YouTube
  │   ├── processed/    # Pistas separadas
  │   └── temp/         # Archivos temporales
  ├── models/           # Modelos de IA
  └── src/
      ├── backend/      # Procesamiento y lógica de negocio
      ├── frontend/     # Interfaz de usuario (futuro)
      ├── models/       # Interfaces de modelos
      └── utils/        # Utilidades
  ```
- [x] Configurar archivos de inicialización de Python

### Implementación de módulos

- [x] Crear archivo de configuración (`src/utils/config.py`)
  - Rutas de directorios
  - Parámetros de audio
  - Configuración de modelos
  
- [x] Implementar descargador de YouTube (`src/backend/youtube_downloader.py`)
  - Obtener información de videos
  - Descargar audio en alta calidad
  - Mostrar progreso de descarga
  
- [x] Implementar procesador de audio (`src/backend/audio_processor.py`)
  - Simulación de separación de pistas
  - Mezcla de pistas con ajustes de volumen
  - Preparación para integración de Demucs
  
- [x] Crear interfaz de línea de comandos (`src/app.py`)
  - Menú de opciones
  - Descarga de audio desde YouTube
  - Procesamiento de archivos locales
  - Mezclado de pistas
  
- [x] Documentar el proyecto
  - README.md con instrucciones de instalación y uso
  - Documentación interna del código

### Pruebas realizadas

- [x] Descargar audio de YouTube
- [x] Simular la separación de pistas
- [x] Crear mezclas personalizadas ajustando volúmenes
- [x] Ejecutar el flujo completo de la aplicación

## Sesión de trabajo (20/05/2025)

### Implementación de Demucs

- [x] Instalar Demucs en el entorno conda
  ```bash
  pip install demucs
  ```
- [x] Actualizar la clase `AudioProcessor` para implementar la separación real
  - [x] Completar la función `separate_tracks()` utilizando Demucs
  - [x] Implementar procesamiento por chunks para optimizar memoria con la función `_separate_chunks()`
  - [x] Añadir soporte para diferentes modelos de Demucs
    - Agregar función `change_model()`
    - Agregar función `get_available_models()`

- [x] Actualizar `app.py` para soportar la funcionalidad de Demucs
  - [x] Añadir opción para cambiar entre modelos
  - [x] Mostrar información del dispositivo utilizado (CPU/GPU)
  - [x] Mejorar la presentación de progreso durante la separación

- [x] Actualizar documentación
  - [x] Actualizar README.md con información sobre modelos disponibles
  - [x] Actualizar progreso del proyecto

### Pruebas realizadas

- [x] Cargar diferentes modelos de Demucs
- [x] Separar pistas de audio con el modelo predeterminado
- [x] Procesar archivos de diferentes duraciones
- [x] Verificar el manejo de memoria para archivos grandes
- [x] Mezclar pistas separadas con ajustes de volumen

## Sesión de trabajo (25/05/2025)

### Optimización de rendimiento

- [x] Implementar detección de hardware
  - [x] Verificar disponibilidad de GPU con `torch.cuda.is_available()`
  - [x] Configurar optimizaciones según hardware detectado
  - [x] Implementar función `get_hardware_info()` para mostrar detalles del sistema

- [x] Optimizar procesamiento para CPU
  - [x] Paralelización con `torch.set_num_threads()`
  - [x] Ajuste automático del tamaño de los segmentos según dispositivo
  - [x] Optimización de memoria usando CPU para almacenamiento intermedio

- [x] Implementar caché de modelos
  - [x] Creación de sistema de caché para evitar recargar modelos
  - [x] Implementación de función `_load_model()` con soporte de caché

### Mejoras de monitoreo y experiencia de usuario

- [x] Mejorar logs y monitoreo de progreso
  - [x] Añadir medición de tiempo en cada fase del proceso
  - [x] Implementar estimación de tiempo restante
  - [x] Añadir timestamps en barra de progreso para confirmación visual

- [x] Mejorar interfaz de línea de comandos
  - [x] Añadir información detallada de hardware
  - [x] Mejorar presentación de opciones y resultados
  - [x] Añadir símbolos visuales para mejor interpretación (✅, ❌, etc.)

- [x] Actualizar dependencias
  - [x] Completar lista de dependencias en requirements.txt
  - [x] Añadir dependencias específicas para optimización

### Pruebas realizadas

- [x] Medir mejora de rendimiento en CPU (reducción de tiempo ~30%)
- [x] Verificar funcionamiento del sistema de caché de modelos
- [x] Comprobar estimaciones de tiempo y progreso
- [x] Procesar archivos de larga duración

## Siguientes pasos

### Mejoras de funcionalidad

- [ ] Implementar opciones de exportación
  - [ ] Diferentes formatos (WAV, MP3, FLAC)
  - [ ] Diferentes calidades
- [ ] Añadir opciones de configuración avanzada
  - [ ] Parámetros de separación
  - [ ] Calidad vs. velocidad
- [ ] Implementar gestión de proyectos
  - [ ] Guardar/cargar proyectos
  - [ ] Historial de archivos recientes

### Interfaz de usuario

- [ ] Configurar entorno de desarrollo React/Electron
- [ ] Diseñar componentes de UI
  - [ ] Reproductor de audio
  - [ ] Visualizador de forma de onda
  - [ ] Controles deslizantes para pistas
- [ ] Integrar backend con frontend
  - [ ] API de comunicación
  - [ ] Gestión de estados
  
### Testing

- [ ] Implementar pruebas unitarias
- [ ] Implementar pruebas de integración
- [ ] Realizar pruebas de rendimiento en diferentes dispositivos 