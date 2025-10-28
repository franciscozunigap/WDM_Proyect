# Guía de Uso Rápido - Simulador EON

## Configuración Inicial (Solo una vez)

```bash
# Hacer ejecutable el script de configuración
chmod +x setup.sh

# Ejecutar configuración automática
./setup.sh

# Activar entorno virtual
source venv/bin/activate
```

## Ejecución de Simulaciones

### Simulación Completa
```bash
python main.py
```
- Ejecuta experimentos completos con todas las cargas de demanda
- Genera gráficos comparativos
- Guarda resultados en archivos

### Pruebas Rápidas
```bash
# Ejecutar todas las pruebas
python test_implementation.py

# Prueba específica de find_first_fit
python -c "
from test_implementation import TestNetworkState
test = TestNetworkState()
test.setup_method()
test.test_find_first_fit_with_occupied_slots()
print('✓ Test find_first_fit pasado')
"
```

### Pruebas Individuales de Módulos
```bash
# Probar topología
python topology.py

# Probar utilidades
python utils.py

# Probar modelo de red
python network_model.py

# Probar algoritmos
python algorithms.py
```

## Interpretación de Resultados

### Archivos Generados
- `eon_simulation_results.png`: Gráficos comparativos
- `simulation_results.txt`: Resultados detallados en texto

### Métricas Clave
- **Watermark**: Slot más alto ocupado en la red (menor es mejor)
- **Probabilidad de Bloqueo**: Fracción de demandas rechazadas (menor es mejor)
- **Utilización**: Fracción del espectro utilizado

### Resultados Esperados
- k-SP-MW debería mostrar menor watermark que SPFF
- La diferencia se hace más notable con cargas altas
- Ambos algoritmos pueden tener probabilidades de bloqueo similares

## Personalización

### Modificar Parámetros
Editar `config.py`:
```python
# Cambiar cargas de demanda
DEMAND_LOADS = [50, 100, 150, 200]

# Cambiar número de ejecuciones
RUNS_PER_LOAD = 10

# Cambiar número de caminos k
K_PATHS = 5
```

### Ejecutar Simulación Personalizada
```python
from main import EONSimulator

# Crear simulador
simulator = EONSimulator()

# Ejecutar solo una carga específica
results = simulator.run_single_experiment(150, seed=42)
print(f"Watermark SPFF: {results['spff']['watermark']}")
print(f"Watermark k-SP-MW: {results['ksp_mw']['watermark']}")
```

## Solución de Problemas

### Error de Importación
```bash
# Verificar que el entorno virtual está activado
which python
# Debería mostrar: .../venv/bin/python

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de Memoria
- Reducir `RUNS_PER_LOAD` en `config.py`
- Reducir `MAX_SLOTS` para pruebas rápidas

### Resultados Inesperados
- Verificar que las pruebas pasan: `python test_implementation.py`
- Revisar logs de consola para errores
- Comprobar que la topología NSFNET se crea correctamente

## Comandos Útiles

```bash
# Ver información de la red
python -c "from topology import get_nsfnet_info; print(get_nsfnet_info())"

# Probar generación de demandas
python -c "from utils import generate_demands; from topology import create_nsfnet; G=create_nsfnet(); print(generate_demands(G, 5))"

# Verificar configuración
python -c "import config; print(f'Slots: {config.MAX_SLOTS}, Cargas: {config.DEMAND_LOADS}')"
```
