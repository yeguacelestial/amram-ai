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

## Siguientes pasos

### Implementación de Demucs

- [ ] Instalar Demucs en el entorno conda
  ```bash
  pip install demucs
  ```
- [ ] Actualizar la clase `AudioProcessor` para implementar la separación real
  - [ ] Completar la función `separate_tracks()` 
  - [ ] Implementar procesamiento por chunks para optimizar memoria
  - [ ] Añadir soporte para diferentes modelos de Demucs

### Optimización de rendimiento

- [ ] Implementar detección de hardware
  - [ ] Verificar disponibilidad de GPU
  - [ ] Seleccionar optimizaciones adecuadas según hardware
- [ ] Optimizar procesamiento para CPU
  - [ ] Paralelización de tareas
  - [ ] Reducción de precisión para dispositivos de gama baja
- [ ] Implementar caché de modelos
  - [ ] Descargar modelos solo cuando se necesiten
  - [ ] Guardar modelos entre sesiones

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