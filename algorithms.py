"""
Módulo de algoritmos para el simulador EON
Implementa los algoritmos SPFF y k-SP-MW para el problema RMLSA
"""

import networkx as nx
from utils import (
    get_k_shortest_paths, 
    get_modulation, 
    get_slots_necesarios, 
    get_path_distance,
    sort_demands
)
from config import K_PATHS


def run_spff(graph, demands, network_state):
    """
    Ejecuta el algoritmo Shortest-Path First-Fit (SPFF)
    
    Args:
        graph (networkx.Graph): Grafo de la red
        demands (list): Lista de demandas (source, target, bandwidth_gbps)
        network_state (NetworkState): Estado actual de la red
        
    Returns:
        dict: Resultados del algoritmo
    """
    # Ordenar demandas por ancho de banda (descendente)
    sorted_demands = sort_demands(demands)
    
    successful_assignments = 0
    blocked_assignments = 0
    
    for source, target, bandwidth in sorted_demands:
        # Encontrar el camino más corto
        try:
            shortest_path = nx.shortest_path(graph, source, target, weight='distance_km')
        except nx.NetworkXNoPath:
            blocked_assignments += 1
            continue
        
        # Calcular distancia del camino
        path_distance = get_path_distance(graph, shortest_path)
        
        if path_distance == float('inf'):
            blocked_assignments += 1
            continue
        
        # Obtener modulación apropiada
        modulation, _ = get_modulation(path_distance)
        
        # Calcular slots necesarios
        slots_needed = get_slots_necesarios(bandwidth, modulation)
        
        # Obtener índices de enlaces del camino
        link_indices = network_state.get_link_indices(shortest_path)
        
        if not link_indices:
            blocked_assignments += 1
            continue
        
        # Buscar primer slot disponible (First-Fit)
        start_slot = network_state.find_first_fit(link_indices, slots_needed)
        
        if start_slot >= 0:
            # Asignar recursos
            success = network_state.asignar_recursos(link_indices, start_slot, slots_needed)
            if success:
                successful_assignments += 1
            else:
                blocked_assignments += 1
        else:
            blocked_assignments += 1
    
    # Actualizar estadísticas de bloqueo
    network_state.blocked_requests += blocked_assignments
    
    return {
        'algorithm': 'SPFF',
        'successful_assignments': successful_assignments,
        'blocked_assignments': blocked_assignments,
        'watermark': network_state.get_watermark(),
        'utilization': network_state.get_utilization(),
        'blocking_probability': blocked_assignments / len(demands) if len(demands) > 0 else 0.0
    }


def run_ksp_mw(graph, demands, network_state):
    """
    Ejecuta el algoritmo k-Shortest-Paths Minimum-Watermark (k-SP-MW)
    
    Args:
        graph (networkx.Graph): Grafo de la red
        demands (list): Lista de demandas (source, target, bandwidth_gbps)
        network_state (NetworkState): Estado actual de la red
        
    Returns:
        dict: Resultados del algoritmo
    """
    # Ordenar demandas por ancho de banda (descendente)
    sorted_demands = sort_demands(demands)
    
    successful_assignments = 0
    blocked_assignments = 0
    
    for source, target, bandwidth in sorted_demands:
        # Obtener k caminos más cortos
        k_paths = get_k_shortest_paths(graph, source, target, K_PATHS)
        
        if not k_paths:
            blocked_assignments += 1
            continue
        
        best_path = None
        best_watermark = float('inf')
        best_start_slot = -1
        best_slots_needed = 0
        
        # Evaluar cada camino
        for path in k_paths:
            # Calcular distancia del camino
            path_distance = get_path_distance(graph, path)
            
            if path_distance == float('inf'):
                continue
            
            # Obtener modulación apropiada
            modulation, _ = get_modulation(path_distance)
            
            # Calcular slots necesarios
            slots_needed = get_slots_necesarios(bandwidth, modulation)
            
            # Obtener índices de enlaces del camino
            link_indices = network_state.get_link_indices(path)
            
            if not link_indices:
                continue
            
            # Buscar primer slot disponible
            start_slot = network_state.find_first_fit(link_indices, slots_needed)
            
            if start_slot >= 0:
                # Simular asignación para calcular watermark resultante
                simulated_watermark = max(network_state.get_watermark(), start_slot + slots_needed)
                
                # Elegir el camino que minimice el watermark
                if simulated_watermark < best_watermark:
                    best_watermark = simulated_watermark
                    best_path = path
                    best_start_slot = start_slot
                    best_slots_needed = slots_needed
        
        # Asignar recursos al mejor camino encontrado
        if best_path is not None:
            link_indices = network_state.get_link_indices(best_path)
            success = network_state.asignar_recursos(link_indices, best_start_slot, best_slots_needed)
            
            if success:
                successful_assignments += 1
            else:
                blocked_assignments += 1
        else:
            blocked_assignments += 1
    
    # Actualizar estadísticas de bloqueo
    network_state.blocked_requests += blocked_assignments
    
    return {
        'algorithm': 'k-SP-MW',
        'successful_assignments': successful_assignments,
        'blocked_assignments': blocked_assignments,
        'watermark': network_state.get_watermark(),
        'utilization': network_state.get_utilization(),
        'blocking_probability': blocked_assignments / len(demands) if len(demands) > 0 else 0.0
    }


def compare_algorithms(graph, demands, network_state_spff, network_state_ksp):
    """
    Compara ambos algoritmos con las mismas demandas
    
    Args:
        graph (networkx.Graph): Grafo de la red
        demands (list): Lista de demandas
        network_state_spff (NetworkState): Estado de red para SPFF
        network_state_ksp (NetworkState): Estado de red para k-SP-MW
        
    Returns:
        dict: Resultados comparativos
    """
    # Ejecutar SPFF
    spff_results = run_spff(graph, demands, network_state_spff)
    
    # Ejecutar k-SP-MW
    ksp_results = run_ksp_mw(graph, demands, network_state_ksp)
    
    return {
        'spff': spff_results,
        'ksp_mw': ksp_results,
        'watermark_improvement': spff_results['watermark'] - ksp_results['watermark'],
        'blocking_improvement': spff_results['blocking_probability'] - ksp_results['blocking_probability']
    }


def get_algorithm_statistics(results):
    """
    Calcula estadísticas de los resultados del algoritmo
    
    Args:
        results (dict): Resultados del algoritmo
        
    Returns:
        dict: Estadísticas calculadas
    """
    total_demands = results['successful_assignments'] + results['blocked_assignments']
    
    stats = {
        'total_demands': total_demands,
        'success_rate': results['successful_assignments'] / total_demands if total_demands > 0 else 0.0,
        'blocking_rate': results['blocked_assignments'] / total_demands if total_demands > 0 else 0.0,
        'watermark': results['watermark'],
        'utilization': results['utilization'],
        'spectrum_efficiency': results['successful_assignments'] / results['watermark'] if results['watermark'] > 0 else 0.0
    }
    
    return stats


if __name__ == "__main__":
    # Prueba básica del módulo
    from topology import create_nsfnet
    from network_model import NetworkState
    from utils import generate_demands
    
    print("Prueba básica de algoritmos:")
    
    # Crear red y generar demandas de prueba
    G = create_nsfnet()
    test_demands = generate_demands(G, 10, seed=42)
    
    print(f"Demandas de prueba: {len(test_demands)}")
    for i, (src, dst, bw) in enumerate(test_demands[:3]):
        print(f"  Demanda {i+1}: {src} -> {dst}, {bw:.1f} Gbps")
    
    # Crear estados de red para ambos algoritmos
    network_spff = NetworkState(G)
    network_ksp = NetworkState(G)
    
    # Ejecutar SPFF
    print("\nEjecutando SPFF...")
    spff_results = run_spff(G, test_demands, network_spff)
    print(f"SPFF - Watermark: {spff_results['watermark']}, Bloqueos: {spff_results['blocked_assignments']}")
    
    # Ejecutar k-SP-MW
    print("\nEjecutando k-SP-MW...")
    ksp_results = run_ksp_mw(G, test_demands, network_ksp)
    print(f"k-SP-MW - Watermark: {ksp_results['watermark']}, Bloqueos: {ksp_results['blocked_assignments']}")
    
    # Comparar resultados
    print(f"\nComparación:")
    print(f"Mejora en watermark: {spff_results['watermark'] - ksp_results['watermark']}")
    print(f"Mejora en probabilidad de bloqueo: {spff_results['blocking_probability'] - ksp_results['blocking_probability']:.3f}")
