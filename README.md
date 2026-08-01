# Crimson Cleaner | TEAM ALUCARD

**Version:** `v0.1.1 Alpha`  
**Dev:** `Killgore793`  

Crimson Cleaner v0.2 Alpha — Stage 1: Cleaning Execution Framework (DRY_RUN_ONLY).

---

## 📌 Visión del Proyecto

**Crimson Cleaner** es un optimizador de memoria RAM y recursos de sistema profesional para Windows, diseñado con una arquitectura modular, limpia y escalable basada en Servicios (Service-Oriented Architecture). 

A diferencia de las herramientas convencionales que realizan liberaciones superficiales de memoria, **Crimson Cleaner** está construido para interactuar con las APIs de bajo nivel del Kernel de Windows (Working Sets, Standby Memory, Page File y Commit Limit).

---

## 🎨 Características de la Versión `v0.1.1 Alpha`

- **Interfaz Moderna Fluent Dark**: Diseñada con bordes redondeados, estética oscura Windows 11, acentos Crimson `#DC143C` y animaciones fluidas.
- **Identidad de Software**: Integración visible de Marca (`TEAM ALUCARD`), Versión (`v0.1.1 Alpha`), Desarrollador (`Dev: Killgore793`) y emblema personalizado.
- **Monitoreo en Tiempo Real (1s)**:
  - RAM Instalada
  - RAM Utilizada (%)
  - RAM Libre
  - Memoria en Caché / Standby
  - Commit Limit
  - Page File (Archivo de Paginación)
  - Uso de CPU (%)
  - Cantidad de Procesos Activos
- **Barra de Distribución de Memoria**: Visualización segmentada e interactiva del consumo de RAM.
- **Botón de Optimización ("Optimizar Memoria")**: Implementación de rutina de prueba asíncrona con señales de progreso y registro de eventos.
- **Sistema Centralizado de Logging**: Registro simultáneo en consola y en archivo persistente (`logs/crimson_cleaner.log`).
- **Sistema de Configuración JSON**: Gestor extensible listo para guardar preferencias de usuario (`config/settings.json`).
- **Análisis Seguro Asíncrono**: Escaneo tipado de temporales, Prefetch, papelera, Windows Update y cachés de navegador, sin cambios en el sistema.

---

## 🛠️ Tecnologías

- **Python**: 3.14+
- **PySide6**: Qt 6 Framework GUI
- **psutil**: Monitoreo de recursos
- **ctypes / pywin32**: Enlace nativo con APIs de Windows
- **pathlib & logging**: Gestión de rutas y logs estandarizada

---

## 📂 Arquitectura del Proyecto

```
CrimsonCleaner/
│
├── main.py                    # Punto de entrada principal
├── app.py                     # Controlador de la aplicación Qt y servicios
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación
│
├── core/                      # Módulos del núcleo del sistema
│   ├── __init__.py
│   ├── logger.py              # Sistema de logs centralizado
│   ├── memory_manager.py      # Gestión de abstracción de memoria
│   ├── process_manager.py     # Gestión e inspección de procesos
│   ├── system_info.py         # Recolección de métricas hardware
│   └── windows_api.py         # Interfaces CTypes / Win32 API
│
├── services/                  # Capa de servicios orientados a tareas
│   ├── __init__.py
│   ├── monitor_service.py     # Servicio de polling en segundo plano (QTimer)
│   ├── optimizer_service.py   # Colector y ejecutor de rutinas de optimización
│   └── update_service.py      # Servicio de actualizaciones (Stub)
│
├── ui/                        # Interfaz gráfica PySide6
│   ├── __init__.py
│   ├── dashboard.py           # Vista principal del panel de control
│   ├── main_window.py         # Ventana contenedora frameless
│   ├── theme.py               # Tokens de diseño y hoja de estilos QSS Fluent
│   ├── resources/             # Recursos adicionales
│   └── widgets/               # Componentes reutilizables
│       ├── custom_button.py   # Botón primario animado
│       ├── header_bar.py      # Barra de título personalizada
│       ├── log_viewer.py      # Consola de eventos en vivo
│       ├── memory_bar.py      # Barra visual de distribución de RAM
│       └── stat_card.py       # Tarjetas métricas
│
├── assets/                    # Emblemas e íconos (logo.png)
├── config/                    # Configuración (settings.json)
└── logs/                      # Archivos de registro (crimson_cleaner.log)
```

---

## 🚀 Instalación y Ejecución

### 1. Requisitos
Tener instalado Python 3.14+ en Windows.

### 2. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecución
```bash
python main.py
```

---

## 🔮 Hoja de Ruta (Futuras Versiones)

En versiones posteriores se integrarán:
- Optimización real de memoria del Kernel
- Limpieza de Standby Memory List
- Trimming de Working Sets de procesos
- Modo Gamer (Modo de alto rendimiento)
- Programador automático de limpiezas
- Diagnóstico inteligente y estadísticas
- Sistema de Plugins e Internacionalización
