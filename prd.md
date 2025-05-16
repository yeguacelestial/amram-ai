# PRD: Amram AI - Clon Local de Moises AI

## 1. Product overview
### 1.1 Document title and version
- PRD: Amram AI - Clon Local de Moises AI
- Versión: 1.0.1

### 1.2 Product summary
Amram AI es una aplicación de escritorio multiplataforma (Windows, macOS, Linux) que permite a los usuarios separar pistas de audio de cualquier canción mediante tecnologías de inteligencia artificial ejecutadas completamente de forma local. La aplicación permite a los usuarios introducir un enlace de YouTube o importar archivos de audio, y automáticamente procesa y separa las diferentes pistas instrumentales (bajo eléctrico, guitarra eléctrica, piano y voz), ofreciendo controles para activar/desactivar cada instrumento.

A diferencia de servicios en la nube como Moises AI, Amram AI ofrece total privacidad y funcionamiento sin conexión, utilizando modelos de IA open source optimizados para ejecutarse en hardware de consumo. La experiencia de usuario se ha diseñado para ser intuitiva, visualmente atractiva y con visualizaciones de ondas completas, brindando una solución simple pero poderosa para músicos, productores y entusiastas del audio.

## 2. Goals
### 2.1 Business goals
- Crear una alternativa local y gratuita a servicios de separación de audio basados en la nube.
- Proporcionar una solución que respete la privacidad del usuario al no enviar datos a servidores externos.
- Optimizar el rendimiento para que funcione en hardware de consumo estándar.
- Establecer una base de código que pueda expandirse con nuevas características en el futuro.

### 2.2 User goals
- Separar pistas de audio de canciones sin necesidad de suscripciones o conexión a internet.
- Desactivar instrumentos específicos (bajo eléctrico, guitarra eléctrica, piano y voz) de cualquier canción.
- Procesar canciones directamente desde YouTube sin pasos intermedios.
- Disfrutar de una interfaz intuitiva y atractiva que facilite el flujo de trabajo.
- Guardar los resultados para uso posterior en formatos de audio estándar.

### 2.3 Non-goals
- Crear un servicio en la nube o basado en suscripciones.
- Competir directamente con todas las funcionalidades avanzadas de Moises AI (como detección de acordes o transposición de tonalidad en esta primera versión).
- Ofrecer edición avanzada de audio más allá de la separación de pistas.
- Proporcionar un DAW (Digital Audio Workstation) completo.
- Optimizar para dispositivos móviles en esta primera fase.

## 3. User personas
### 3.1 Key user types
- Músicos amateur y profesionales
- Productores de música
- Estudiantes de música
- Entusiastas del karaoke
- Creadores de contenido

### 3.2 Basic persona details
- **Miguel**: Guitarrista amateur que busca practicar sobre canciones sin la pista de guitarra original.
- **Laura**: Cantante que desea crear pistas de karaoke personalizadas eliminando las voces de sus canciones favoritas.
- **Carlos**: Productor musical indie que necesita aislar elementos específicos de referencias musicales para sus composiciones.
- **Ana**: Estudiante de música que analiza la estructura de canciones aislando diferentes instrumentos.
- **Roberto**: Creador de contenido que necesita extraer pistas instrumentales para sus videos.

### 3.3 Role-based access
- **Usuario estándar**: Acceso completo a todas las funcionalidades de la aplicación local.

## 4. Functional requirements
- **Descarga de videos de YouTube** (Prioridad: Alta)
  - Permitir al usuario pegar URLs de YouTube directamente en la aplicación.
  - Mostrar información básica del video (título, duración, miniatura) antes de procesar.
  - Descargar automáticamente el audio en alta calidad.

- **Separación de pistas de audio** (Prioridad: Alta)
  - Separar el audio en pistas individuales: voz, bajo eléctrico, guitarra eléctrica, piano y otros instrumentos.
  - Permitir la visualización de forma de onda para cada pista separada.
  - Ofrecer controles de volumen individuales para cada instrumento.
  - Permitir silenciar/activar cada pista individualmente.

- **Interfaz de usuario** (Prioridad: Alta)
  - Diseñar una interfaz moderna e intuitiva.
  - Incluir visualizaciones de forma de onda para cada pista.
  - Proporcionar controles de reproducción estándar (reproducir, pausar, detener, avanzar, retroceder).
  - Implementar controles deslizantes para volumen de cada pista.

- **Gestión de archivos** (Prioridad: Media)
  - Guardar proyectos para edición posterior.
  - Exportar pistas individuales o mezclas personalizadas como archivos de audio (WAV, MP3).
  - Organizar proyectos en una biblioteca de fácil navegación.

- **Optimización de rendimiento** (Prioridad: Alta)
  - Implementar procesamiento en GPU cuando esté disponible.
  - Ofrecer diferentes niveles de calidad/velocidad según el hardware del usuario.
  - Mostrar indicadores de progreso durante el procesamiento.

## 5. User experience
### 5.1. Entry points & first-time user flow
- Instalación sencilla mediante un instalador estándar para la plataforma del usuario.
- Primera ejecución con un breve tutorial que muestra las principales funcionalidades.
- Pantalla inicial con campo prominente para pegar URL de YouTube.
- Opción para abrir un proyecto anterior directamente desde la pantalla de inicio.
- Verificación automática de requisitos técnicos al iniciar por primera vez.

### 5.2. Core experience
- **Ingreso de URL**: El usuario pega una URL de YouTube en el campo designado y hace clic en "Procesar".
  - La interfaz muestra una miniatura y datos del video para confirmar que es el correcto.
- **Descarga y procesamiento**: La aplicación descarga el audio y muestra una barra de progreso.
  - Se muestran estimaciones de tiempo restante y se permite cancelar si es necesario.
- **Interfaz de editor**: Una vez procesado, se muestra la interfaz principal con todas las pistas separadas.
  - Cada pista tiene controles de volumen y un botón para activar/desactivar.
- **Reproducción y ajuste**: El usuario reproduce la mezcla y ajusta los niveles de cada instrumento.
  - Los cambios se escuchan en tiempo real para facilitar la experiencia.
- **Exportación**: El usuario puede guardar la mezcla personalizada o pistas individuales.
  - Se ofrecen opciones de formato y calidad antes de la exportación final.

### 5.3. Advanced features & edge cases
- Procesamiento por lotes para múltiples canciones.
- Modo offline para procesar archivos de audio locales cuando no hay conexión a internet.
- Manejo de errores cuando el video de YouTube no está disponible o tiene restricciones.
- Opciones avanzadas para ajustar parámetros del algoritmo de separación.
- Recuperación automática en caso de cierres inesperados.
- Detección y advertencia de hardware insuficiente.

### 5.4. UI/UX highlights
- Tema oscuro por defecto optimizado para uso nocturno con opción de tema claro.
- Visualizaciones de espectrograma en tiempo real para cada pista.
- Diseño responsive que se adapta a diferentes resoluciones de pantalla.
- Atajos de teclado para todas las funciones principales.
- Interfaz modular que permite reordenar componentes según preferencias.
- Animaciones sutiles para transiciones entre estados de la aplicación.

## 6. Narrative
Miguel es un guitarrista amateur que quiere mejorar su técnica practicando con sus canciones favoritas. Descubre Amram AI y con solo pegar un enlace de YouTube, puede silenciar la guitarra de cualquier canción para tocar junto con la banda original. Le encanta la simplicidad del proceso y la calidad de la separación, que le permite escuchar claramente los otros instrumentos mientras practica su parte. Gracias a Amram AI, Miguel ha acelerado significativamente su aprendizaje sin gastar en suscripciones mensuales ni preocuparse por su privacidad.

## 7. Success metrics
### 7.1. User-centric metrics
- Tiempo promedio para completar el flujo desde URL hasta reproducción de pistas separadas (objetivo: <2 minutos).
- Porcentaje de usuarios que completan exitosamente el flujo de procesamiento sin errores (objetivo: >95%).
- Valoración de calidad de separación por parte de los usuarios (objetivo: >4.5/5).
- Número de proyectos guardados por usuario (indicador de uso continuo).
- Tasa de retención a los 30 días (objetivo: >70%).

### 7.2. Business metrics
- Número de instalaciones activas.
- Contribuciones al proyecto open source (para medir la comunidad).
- Menciones y reseñas en medios especializados.
- Uso de recursos computacionales por procesamiento (para optimizaciones).

### 7.3. Technical metrics
- Tiempo promedio de procesamiento por minuto de audio (objetivo: <1 minuto de procesamiento por minuto de audio en hardware medio).
- Uso de memoria y CPU durante el procesamiento.
- Tasa de errores durante la descarga y procesamiento de videos.
- Precisión de la separación de instrumentos comparada con soluciones comerciales.

## 8. Technical considerations
### 8.1. Integration points
- API de YouTube y biblioteca yt-dlp para obtener metadatos y descargar videos manteniendo la calidad original.
- Frameworks de procesamiento de audio como PyTorch para ejecutar modelos de IA de separación (Demucs, Spleeter).
- Bibliotecas de visualización de audio como Waveform.js o Wavesurfer.js para las formas de onda y espectrogramas.
- Sistema de archivos local para almacenamiento de proyectos y exportaciones.
- Electron para el empaquetado multiplataforma y acceso a funcionalidades nativas.
- React para la interfaz de usuario moderna y reactiva.
- Posible integración con DAWs populares mediante exportación en formatos compatibles.

### 8.2. Data storage & privacy
- Almacenamiento local de todos los archivos de audio y proyectos.
- Sin envío de datos de usuario a servidores externos.
- Gestión de permisos mínimos necesarios (acceso a sistema de archivos).
- Almacenamiento en caché inteligente para optimizar espacio en disco.
- Opción para ubicación personalizada de la biblioteca de proyectos.

### 8.3. Scalability & performance
- Optimización para procesamiento en GPU utilizando CUDA o similares cuando esté disponible.
- Procesamiento por lotes para múltiples archivos.
- Ajustes de calidad/rendimiento para adaptarse a diferentes capacidades de hardware.
- Uso de modelos pre-entrenados optimizados para CPU para usuarios sin GPU.
- Procesos de Python independientes para las tareas de separación intensivas evitando bloquear la interfaz.
- Procesamiento paralelo para aprovechar CPUs multinúcleo.
- Compresión eficiente para archivos de proyecto y exportaciones.

### 8.4. Potential challenges
- Calidad de separación en hardware limitado puede ser inferior a soluciones en la nube.
- Problemas legales potenciales relacionados con la descarga de contenido de YouTube.
- Variabilidad en la calidad de separación dependiendo del tipo de música y mezcla original.
- Requisitos de hardware que podrían excluir equipos más antiguos.
- Mantenimiento de compatibilidad con cambios en la API de YouTube.
- Tamaño de los modelos de IA y requerimientos de almacenamiento.

## 9. Milestones & sequencing
### 9.1. Project estimate
- Medio-Grande: 3-4 meses para una versión inicial funcional.

### 9.2. Team size & composition
- Equipo Medio: 3-5 personas
  - 2-3 desarrolladores (1 especialista en IA/audio para Python, 1-2 desarrolladores frontend con React/Electron)
  - 1 diseñador UI/UX
  - 1 QA/tester con conocimientos musicales

### 9.3. Suggested phases
- **Fase 1**: Investigación y prueba de concepto (2-3 semanas)
  - Evaluación de modelos de IA open source para separación de audio (principalmente Demucs v4)
  - Pruebas de rendimiento en diferentes configuraciones de hardware
  - Diseño de arquitectura del sistema (Electron + React + Python)
  - Prototipos de interfaz de usuario con React

- **Fase 2**: Desarrollo del núcleo de procesamiento (4-5 semanas)
  - Implementación del sistema de descarga de YouTube con yt-dlp
  - Integración del modelo Demucs para separación de audio
  - Desarrollo de la pipeline de procesamiento en Python
  - Configuración de comunicación entre frontend (Electron/React) y backend (Python)
  - Optimizaciones de rendimiento iniciales

- **Fase 3**: Desarrollo de la interfaz de usuario (4-5 semanas)
  - Implementación del diseño de UI/UX en React
  - Desarrollo de visualizaciones de audio con Waveform.js/Wavesurfer.js
  - Implementación de controles de reproducción y edición
  - Integración con el núcleo de procesamiento
  - Desarrollo de temas (claro/oscuro) y sistema de estilos

- **Fase 4**: Integración y pruebas (3-4 semanas)
  - Ensamblaje de todos los componentes
  - Pruebas de rendimiento y optimización
  - Corrección de bugs y refinamiento de la experiencia de usuario
  - Preparación del sistema de empaquetado e instalación con Electron-builder
  - Pruebas de instalación en diferentes plataformas

## 10. User stories
### 10.1. Descargar audio de YouTube
- **ID**: US-001
- **Description**: Como usuario, quiero pegar un enlace de YouTube en la aplicación para que descargue automáticamente el audio de alta calidad.
- **Acceptance criteria**:
  - La aplicación acepta enlaces de YouTube válidos.
  - Muestra información del video (título, duración, miniatura) antes de procesar.
  - Descarga el audio en formato de alta calidad.
  - Maneja errores como enlaces inválidos o videos no disponibles.
  - Muestra progreso de descarga en tiempo real.

### 10.2. Procesar y separar pistas de audio
- **ID**: US-002
- **Description**: Como usuario, quiero que la aplicación separe automáticamente el audio en pistas individuales (voz, bajo, guitarra, piano, otros).
- **Acceptance criteria**:
  - El audio descargado se procesa utilizando IA para separar instrumentos.
  - Se generan pistas individuales para voz, bajo eléctrico, guitarra eléctrica, piano y otros instrumentos.
  - Se muestra progreso del procesamiento con estimación de tiempo.
  - El procesamiento aprovecha aceleración por hardware cuando está disponible.
  - El resultado mantiene calidad de audio aceptable en cada pista.

### 10.3. Controlar reproducción de pistas
- **ID**: US-003
- **Description**: Como usuario, quiero controlar la reproducción de las pistas separadas para escuchar combinaciones específicas de instrumentos.
- **Acceptance criteria**:
  - Cada pista tiene controles individuales de volumen y silencio.
  - Hay controles de reproducción estándar (play, pause, stop, seek).
  - Los cambios en los controles afectan la reproducción en tiempo real.
  - Se visualiza la forma de onda de cada pista durante la reproducción.
  - Se muestra una línea de tiempo con marcador de posición actual.

### 10.4. Guardar y cargar proyectos
- **ID**: US-004
- **Description**: Como usuario, quiero guardar mi proyecto actual para continuar trabajando en él más tarde.
- **Acceptance criteria**:
  - Los proyectos se pueden guardar en formato propio de la aplicación.
  - Se guarda el estado de todas las pistas y configuraciones.
  - Los proyectos guardados aparecen en una lista de recientes en la pantalla inicial.
  - Los archivos de proyecto contienen metadatos como título, fecha y fuente.
  - La carga de proyectos restaura exactamente el mismo estado en que se guardaron.

### 10.5. Exportar audio procesado
- **ID**: US-005
- **Description**: Como usuario, quiero exportar mi mezcla personalizada o pistas individuales en formatos de audio estándar.
- **Acceptance criteria**:
  - Se pueden exportar pistas individuales separadas.
  - Se puede exportar la mezcla completa con la configuración actual.
  - Se ofrecen múltiples formatos de exportación (WAV, MP3).
  - Se pueden configurar parámetros de calidad para la exportación.
  - Los archivos exportados incluyen metadatos básicos (título, artista).

### 10.6. Visualizar espectro de audio
- **ID**: US-006
- **Description**: Como usuario, quiero ver representaciones visuales del audio para identificar partes específicas de la canción.
- **Acceptance criteria**:
  - Cada pista muestra su forma de onda a lo largo del tiempo.
  - Se ofrece visualización de espectrograma opcional.
  - Las visualizaciones se actualizan en tiempo real durante la reproducción.
  - Se pueden hacer zoom in/out en la línea de tiempo.
  - Las representaciones visuales son precisas y ayudan a identificar secciones.

### 10.7. Personalizar la interfaz
- **ID**: US-007
- **Description**: Como usuario, quiero personalizar aspectos de la interfaz para adaptarla a mis preferencias.
- **Acceptance criteria**:
  - Se puede cambiar entre tema claro y oscuro.
  - Se puede reordenar la disposición de pistas en la interfaz.
  - Se pueden guardar diferentes layouts de interfaz.
  - Se pueden configurar atajos de teclado personalizados.
  - Los ajustes de interfaz persisten entre sesiones.

### 10.8. Procesar archivos locales
- **ID**: US-008
- **Description**: Como usuario, quiero poder procesar archivos de audio que ya tengo en mi sistema, sin necesidad de YouTube.
- **Acceptance criteria**:
  - Se aceptan formatos comunes de audio (MP3, WAV, FLAC).
  - El flujo de procesamiento es idéntico al de archivos de YouTube.
  - Se pueden arrastrar y soltar archivos a la interfaz.
  - Se muestran propiedades básicas del archivo antes de procesar.
  - El rendimiento es similar o mejor que con archivos de YouTube.

### 10.9. Configurar parámetros de procesamiento
- **ID**: US-009
- **Description**: Como usuario avanzado, quiero ajustar parámetros del algoritmo de separación para optimizar resultados.
- **Acceptance criteria**:
  - Existe una sección de configuración avanzada accesible desde la interfaz principal.
  - Se pueden modificar parámetros como intensidad de separación, calidad vs. velocidad.
  - Los cambios en configuración se reflejan en nuevos procesamientos.
  - Hay preajustes para diferentes tipos de música (rock, jazz, clásica, etc.).
  - Se incluyen descripciones de cada parámetro para usuarios no técnicos.

### 10.10. Primera experiencia de usuario
- **ID**: US-010
- **Description**: Como nuevo usuario, quiero un proceso de introducción que me enseñe a usar las funciones principales.
- **Acceptance criteria**:
  - Al primer inicio se muestra un tutorial interactivo.
  - El tutorial cubre las funciones básicas paso a paso.
  - Se puede saltar o acceder posteriormente al tutorial.
  - Se incluyen ejemplos de uso típicos.
  - El usuario puede probar funcionalidades durante el tutorial. 