# 🎵 Amram AI

Amram AI es una aplicación de escritorio que permite separar pistas de audio de canciones mediante tecnologías de inteligencia artificial ejecutadas completamente de forma local. 

## 🚀 Características

- Separación de pistas de audio (voz, bajo eléctrico, guitarra, batería, piano, etc.)
- Descarga directa de audio desde YouTube
- Controles de volumen independientes para cada instrumento
- Funcionamiento 100% local sin necesidad de conexión a internet
- Interfaz intuitiva y visualización de ondas de audio

## 📋 Estado del Proyecto

Este proyecto se encuentra actualmente en fase de desarrollo (Fase 1: Prueba de concepto). Esta primera fase consiste en la evaluación de modelos de IA open source para separación de audio, pruebas de rendimiento y diseño de la arquitectura del sistema.

### Progreso actual

- [x] Configuración del entorno de desarrollo con conda
- [x] Implementación básica del descargador de YouTube
- [x] Simulación de separación de pistas (para prueba de concepto)
- [x] Interfaz de línea de comandos para pruebas
- [ ] Implementación de Demucs para separación real de pistas
- [ ] Optimización de rendimiento para hardware de consumo
- [ ] Interfaz gráfica con React/Electron

## 🔧 Instalación

### Requisitos previos

- Python 3.10 o superior
- Conda (para gestionar entornos virtuales)
- FFmpeg (para procesamiento de audio)

### Configuración del entorno

1. Clone el repositorio:
   ```bash
   git clone https://github.com/yourusername/amram-ai.git
   cd amram-ai
   ```

2. Cree un entorno conda con los paquetes necesarios:
   ```bash
   conda create -n amram-ai python=3.10
   conda activate amram-ai
   conda install -c conda-forge pytorch torchaudio librosa yt-dlp pyyaml
   pip install demucs
   ```

3. Ejecute la prueba de concepto:
   ```bash
   python src/app.py
   ```

## 🎯 Uso

La versión actual de prueba de concepto permite:

1. Descargar audio desde YouTube proporcionando una URL
2. Simular la separación de pistas de audio
3. Ajustar los niveles de volumen de cada pista
4. Mezclar las pistas con configuraciones personalizadas

## 🗺️ Hoja de ruta

- **Fase 1** (actual): Investigación y prueba de concepto
  - Evaluación de modelos de IA para separación de audio
  - Pruebas de rendimiento
  - Diseño de arquitectura

- **Fase 2**: Desarrollo del núcleo de procesamiento
  - Implementación del sistema de descarga de YouTube
  - Integración del modelo Demucs para separación de audio
  - Optimizaciones de rendimiento

- **Fase 3**: Desarrollo de la interfaz de usuario
  - Implementación del diseño de UI/UX en React
  - Visualizaciones de audio
  - Controles de reproducción y edición

- **Fase 4**: Integración y pruebas
  - Ensamblaje de componentes
  - Optimización
  - Empaquetado para distribución

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue para discutir los cambios importantes antes de crear un pull request.

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para detalles.
