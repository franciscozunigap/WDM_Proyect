# Simulador de Redes Ópticas Elásticas (EONs)
## RMLSA - Routing, Modulation, and Spectrum Assignment

Este proyecto implementa un simulador completo para Redes Ópticas Elásticas (EONs) que compara dos algoritmos para el problema RMLSA estático:

### Algoritmos Implementados
1. **SPFF (Shortest-Path First-Fit)**: Algoritmo de referencia que utiliza el camino más corto y asigna el primer slot disponible
2. **k-SP-MW (k-Shortest-Paths Minimum-Watermark)**: Algoritmo heurístico personalizado que evalúa k caminos y selecciona el que minimiza el watermark

### Objetivo Principal
**Minimizar el watermark del espectro** (Objetivo #3) para optimizar el uso de recursos espectrales en la red.

### Características del Simulador
- **Topología**: NSFNET (14 nodos, 21 enlaces) con distancias realistas
- **Espectro**: 320 slots por enlace, 12.5 GHz por slot
- **Modulaciones**: BPSK, QPSK, 8-QAM, 16-QAM con alcances específicos
- **Experimentos**: Múltiples cargas de demanda con promedios estadísticos
- **Visualización**: Gráficos comparativos de rendimiento

### Estructura del Proyecto
```
├── setup.sh              # Script de configuración del entorno
├── requirements.txt       # Dependencias de Python
├── config.py             # Parámetros de configuración
├── topology.py           # Creación de la red NSFNET
├── utils.py              # Funciones auxiliares
├── network_model.py      # Modelo de estado de la red
├── algorithms.py         # Implementación de SPFF y k-SP-MW
├── main.py              # Simulador principal
└── test_implementation.py # Pruebas unitarias
```

### Instalación y Uso

1. **Configurar entorno**:
   ```bash
   ./setup.sh
   source venv/bin/activate
   ```

2. **Ejecutar simulación**:
   ```bash
   python main.py
   ```

3. **Ejecutar pruebas**:
   ```bash
   python test_implementation.py
   # o con pytest:
   pytest test_implementation.py -v
   ```

### Parámetros de Configuración
- **Cargas de demanda**: [100, 150, 200, 250, 300]
- **Ejecuciones por carga**: 30
- **Rango de ancho de banda**: 50-400 Gbps
- **k caminos**: 3 (para k-SP-MW)

### Resultados Esperados
El simulador genera:
- Gráfico de Carga vs Watermark
- Gráfico de Carga vs Probabilidad de Bloqueo
- Archivo de resultados detallados
- Resumen estadístico en consola

### Dependencias
- `networkx`: Manipulación de grafos
- `numpy`: Cálculos numéricos
- `matplotlib`: Visualización
- `pytest`: Pruebas unitarias

