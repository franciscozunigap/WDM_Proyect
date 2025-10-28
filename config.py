"""
Configuración del simulador de Redes Ópticas Elásticas (EONs)
Proyecto RMLSA - Routing, Modulation, and Spectrum Assignment
"""

# Parámetros de la topología NSFNET
NSFNET_NODES = 14
NSFNET_LINKS = 14

# Parámetros del espectro
MAX_SLOTS = 320  # Total de slots por enlace
SLOT_WIDTH_GHZ = 12.5  # Ancho de banda por slot en GHz
GUARD_BAND_SLOTS = 1  # Slots de banda de guarda

# Tabla de modulación: (distancia_máxima_km, eficiencia_espectral_bits_per_Hz)
MODULATION_TABLE = {
    'BPSK': (4000, 1),    # BPSK: 4000 km, 1 bit/s/Hz
    'QPSK': (2000, 2),    # QPSK: 2000 km, 2 bits/s/Hz
    '8-QAM': (1000, 3),   # 8-QAM: 1000 km, 3 bits/s/Hz
    '16-QAM': (500, 4)    # 16-QAM: 500 km, 4 bits/s/Hz
}

# Parámetros del algoritmo heurístico
K_PATHS = 3  # Número de caminos k para el algoritmo k-SP-MW

# Parámetros del experimento
DEMAND_LOADS = [50, 100, 150, 200]  # Cargas de demanda a simular (reducidas para pruebas)
RUNS_PER_LOAD = 5  # Número de ejecuciones para promediar por punto de carga (reducido para pruebas)
DEMAND_BW_RANGE = (50, 400)  # Rango de ancho de banda de demanda en Gbps

# Parámetros adicionales para la generación de demandas
MIN_DEMAND_BW = DEMAND_BW_RANGE[0]
MAX_DEMAND_BW = DEMAND_BW_RANGE[1]

# Configuración de visualización
PLOT_FIGURE_SIZE = (12, 8)
PLOT_DPI = 300
PLOT_STYLE = 'seaborn-v0_8'

# Configuración de logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
