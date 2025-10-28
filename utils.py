"""
Módulo de utilidades para el simulador EON
Contiene funciones auxiliares para modulación, cálculo de slots y generación de demandas
"""

import random
import networkx as nx
from config import MODULATION_TABLE, GUARD_BAND_SLOTS, MIN_DEMAND_BW, MAX_DEMAND_BW


def get_modulation(distance_km):
    """
    Obtiene el formato de modulación más eficiente para una distancia dada
    
    Args:
        distance_km (float): Distancia en kilómetros
        
    Returns:
        tuple: (nombre_modulacion, eficiencia_espectral)
    """
    # Ordenar modulaciones por eficiencia espectral (descendente)
    sorted_modulations = sorted(MODULATION_TABLE.items(), 
                              key=lambda x: x[1][1], reverse=True)
    
    # Encontrar la modulación con mayor alcance que soporte la distancia
    for mod_name, (max_distance, efficiency) in sorted_modulations:
        if distance_km <= max_distance:
            return mod_name, efficiency
    
    # Si ninguna modulación soporta la distancia, usar BPSK (mayor alcance)
    return 'BPSK', MODULATION_TABLE['BPSK'][1]


def get_slots_necesarios(demanda_gbps, modulacion):
    """
    Calcula el número total de slots necesarios para una demanda
    
    Args:
        demanda_gbps (float): Ancho de banda de la demanda en Gbps
        modulacion (str): Nombre del formato de modulación
        
    Returns:
        int: Número total de slots necesarios (incluyendo banda de guarda)
    """
    if modulacion not in MODULATION_TABLE:
        raise ValueError(f"Modulación {modulacion} no válida")
    
    _, eficiencia = MODULATION_TABLE[modulacion]
    
    # Calcular slots necesarios para la demanda
    # Cada slot tiene 12.5 GHz de ancho de banda
    slots_demanda = demanda_gbps / (eficiencia * 12.5)
    
    # Agregar slots de banda de guarda
    slots_totales = int(slots_demanda) + GUARD_BAND_SLOTS
    
    return max(1, slots_totales)  # Mínimo 1 slot


def generate_demands(graph, num_demands, seed=None):
    """
    Genera una lista de demandas aleatorias para la simulación
    
    Args:
        graph (networkx.Graph): Grafo de la red
        num_demands (int): Número de demandas a generar
        seed (int): Semilla para reproducibilidad (opcional)
        
    Returns:
        list: Lista de tuplas (source, target, bandwidth_gbps)
    """
    if seed is not None:
        random.seed(seed)
    
    demands = []
    nodes = list(graph.nodes())
    
    for _ in range(num_demands):
        # Seleccionar nodos origen y destino aleatorios (diferentes)
        source = random.choice(nodes)
        target = random.choice([n for n in nodes if n != source])
        
        # Generar ancho de banda aleatorio en el rango especificado
        bandwidth = random.uniform(MIN_DEMAND_BW, MAX_DEMAND_BW)
        
        demands.append((source, target, bandwidth))
    
    return demands


def get_path_distance(graph, path):
    """
    Calcula la distancia total de un camino en la red
    
    Args:
        graph (networkx.Graph): Grafo de la red
        path (list): Lista de nodos que forman el camino
        
    Returns:
        float: Distancia total en kilómetros
    """
    if len(path) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(path) - 1):
        source = path[i]
        target = path[i + 1]
        
        if graph.has_edge(source, target):
            total_distance += graph[source][target]['distance_km']
        else:
            # Si no hay enlace directo, usar distancia euclidiana aproximada
            # Esto no debería ocurrir en un camino válido
            return float('inf')
    
    return total_distance


def sort_demands(demands, graph=None, strategy='bandwidth'):
    """
    Ordena las demandas según diferentes estrategias
    
    Args:
        demands (list): Lista de tuplas (source, target, bandwidth_gbps)
        graph (networkx.Graph): Grafo de la red (opcional, necesario para algunas estrategias)
        strategy (str): Estrategia de ordenamiento:
            - 'bandwidth': Por ancho de banda descendente (default)
            - 'smart': Considera bandwidth y longitud de camino
            - 'random': Aleatorio (requiere shuffle previo)
        
    Returns:
        list: Lista ordenada de demandas
    """
    if strategy == 'bandwidth' or graph is None:
        # Ordenamiento por ancho de banda (descendente)
        return sorted(demands, key=lambda x: x[2], reverse=True)
    
    elif strategy == 'smart':
        # Ordenamiento inteligente: considera bandwidth Y dificultad de enrutamiento
        def smart_key(demand):
            source, target, bandwidth = demand
            try:
                # Calcular longitud del camino más corto
                path_length = nx.shortest_path_length(graph, source, target, weight='distance_km')
            except nx.NetworkXNoPath:
                path_length = float('inf')
            
            # Score combinado: priorizar grandes anchos de banda en caminos largos
            # (estas son las demandas más difíciles)
            score = bandwidth * 100 + path_length * 0.01
            return -score  # Negativo para orden descendente
        
        return sorted(demands, key=smart_key)
    
    else:
        # Default: por bandwidth
        return sorted(demands, key=lambda x: x[2], reverse=True)


def get_k_shortest_paths(graph, source, target, k):
    """
    Obtiene los k caminos más cortos entre dos nodos
    
    Args:
        graph (networkx.Graph): Grafo de la red
        source (int): Nodo origen
        target (int): Nodo destino
        k (int): Número de caminos a obtener
        
    Returns:
        list: Lista de caminos (cada camino es una lista de nodos)
    """
    try:
        # Verificar conectividad básica primero
        if not nx.has_path(graph, source, target):
            return []
        
        # Usar el algoritmo de Yen para k caminos más cortos
        # Limitar el número de caminos para evitar bucles infinitos
        paths = []
        path_generator = nx.shortest_simple_paths(graph, source, target, weight='distance_km')
        
        for i, path in enumerate(path_generator):
            if i >= k:
                break
            paths.append(path)
            
            # Limitar la longitud del camino para evitar caminos muy largos
            if len(path) > 20:  # NSFNET tiene máximo 14 nodos
                break
        
        return paths
    except nx.NetworkXNoPath:
        return []
    except nx.NetworkXError:
        return []
    except Exception:
        # Fallback: usar solo el camino más corto
        try:
            shortest_path = nx.shortest_path(graph, source, target, weight='distance_km')
            return [shortest_path]
        except:
            return []


def calculate_path_cost(graph, path, bandwidth_gbps):
    """
    Calcula el "costo" de un camino considerando modulación y slots necesarios
    
    Args:
        graph (networkx.Graph): Grafo de la red
        path (list): Lista de nodos que forman el camino
        bandwidth_gbps (float): Ancho de banda de la demanda
        
    Returns:
        tuple: (distancia_total, modulacion, slots_necesarios)
    """
    if len(path) < 2:
        return float('inf'), None, 0
    
    # Calcular distancia total del camino
    distance = get_path_distance(graph, path)
    
    if distance == float('inf'):
        return distance, None, 0
    
    # Obtener modulación apropiada
    modulation, _ = get_modulation(distance)
    
    # Calcular slots necesarios
    slots_needed = get_slots_necesarios(bandwidth_gbps, modulation)
    
    return distance, modulation, slots_needed


def validate_demand(graph, source, target):
    """
    Valida si existe un camino válido entre dos nodos
    
    Args:
        graph (networkx.Graph): Grafo de la red
        source (int): Nodo origen
        target (int): Nodo destino
        
    Returns:
        bool: True si existe un camino válido
    """
    try:
        nx.shortest_path_length(graph, source, target)
        return True
    except nx.NetworkXNoPath:
        return False


def get_network_statistics(graph):
    """
    Obtiene estadísticas básicas de la red
    
    Args:
        graph (networkx.Graph): Grafo de la red
        
    Returns:
        dict: Diccionario con estadísticas de la red
    """
    stats = {
        'num_nodes': graph.number_of_nodes(),
        'num_edges': graph.number_of_edges(),
        'density': nx.density(graph),
        'is_connected': nx.is_connected(graph),  # Para grafos no dirigidos
        'average_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes(),
        'min_distance': min(data['distance_km'] for _, _, data in graph.edges(data=True)),
        'max_distance': max(data['distance_km'] for _, _, data in graph.edges(data=True)),
        'total_distance': sum(data['distance_km'] for _, _, data in graph.edges(data=True))
    }
    
    return stats


if __name__ == "__main__":
    # Pruebas básicas del módulo
    from topology import create_nsfnet
    
    G = create_nsfnet()
    
    # Probar funciones de modulación
    print("Pruebas de modulación:")
    for distance in [100, 500, 1000, 2000, 3000]:
        mod, eff = get_modulation(distance)
        slots = get_slots_necesarios(100, mod)
        print(f"Distancia {distance}km -> {mod} ({eff} bits/s/Hz) -> {slots} slots")
    
    # Probar generación de demandas
    print("\nPruebas de generación de demandas:")
    demands = generate_demands(G, 5, seed=42)
    for i, (src, dst, bw) in enumerate(demands):
        print(f"Demanda {i+1}: {src} -> {dst}, {bw:.1f} Gbps")
    
    # Probar cálculo de caminos
    print("\nPruebas de caminos:")
    paths = get_k_shortest_paths(G, 0, 5, 3)
    for i, path in enumerate(paths):
        distance = get_path_distance(G, path)
        print(f"Camino {i+1}: {path} (distancia: {distance:.1f} km)")
