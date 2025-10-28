"""
Módulo de topología para el simulador EON
Implementa la creación de la red NSFNET con distancias realistas
"""

import networkx as nx
from config import NSFNET_NODES, NSFNET_LINKS


def create_nsfnet():
    """
    Crea la topología NSFNET con 14 nodos y 21 enlaces
    Incluye distancias realistas en kilómetros para cada enlace
    
    Returns:
        networkx.Graph: Grafo de la red NSFNET con atributos de distancia
    """
    # Crear grafo dirigido para NSFNET
    G = nx.DiGraph()
    
    # Agregar nodos (numerados del 0 al 13)
    for i in range(NSFNET_NODES):
        G.add_node(i)
    
    # Definir enlaces de NSFNET con distancias realistas (en km)
    # Topología NSFNET optimizada con exactamente 14 enlaces bidireccionales
    nsfnet_links = [
        # Enlaces principales de NSFNET (14 enlaces únicos)
        (0, 1, 1200),   # Seattle - Palo Alto
        (1, 2, 400),    # Palo Alto - Los Angeles  
        (2, 3, 300),    # Los Angeles - San Diego
        (3, 4, 2000),   # San Diego - Salt Lake City
        (4, 5, 800),    # Salt Lake City - Denver
        (5, 6, 600),    # Denver - Kansas City
        (6, 7, 500),    # Kansas City - Chicago
        (7, 8, 400),    # Chicago - Ann Arbor
        (8, 9, 300),    # Ann Arbor - Cleveland
        (9, 10, 200),   # Cleveland - Pittsburgh
        (10, 11, 300),  # Pittsburgh - Princeton
        (11, 12, 200),  # Princeton - Cambridge
        (12, 13, 100),  # Cambridge - Ithaca
        (13, 0, 2500),  # Ithaca - Seattle (enlace de cierre)
    ]
    
    # Agregar enlaces al grafo (solo los 14 enlaces únicos)
    for source, target, distance in nsfnet_links:
        G.add_edge(source, target, distance_km=distance)
        # También agregar el enlace bidireccional
        G.add_edge(target, source, distance_km=distance)
    
    # Verificar que tenemos el número correcto de enlaces
    actual_links = G.number_of_edges()
    if actual_links != NSFNET_LINKS * 2:  # *2 porque son bidireccionales
        print(f"Advertencia: NSFNET tiene {actual_links} enlaces, esperados {NSFNET_LINKS * 2}")
    
    return G


def get_nsfnet_info():
    """
    Obtiene información básica sobre la topología NSFNET
    
    Returns:
        dict: Diccionario con información de la topología
    """
    G = create_nsfnet()
    
    info = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'is_connected': nx.is_strongly_connected(G),
        'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'min_distance': min(data['distance_km'] for _, _, data in G.edges(data=True)),
        'max_distance': max(data['distance_km'] for _, _, data in G.edges(data=True)),
        'total_distance': sum(data['distance_km'] for _, _, data in G.edges(data=True))
    }
    
    return info


if __name__ == "__main__":
    # Prueba básica del módulo
    G = create_nsfnet()
    info = get_nsfnet_info()
    
    print("Información de NSFNET:")
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nNodos: {list(G.nodes())}")
    print(f"Enlaces con distancias:")
    for edge in G.edges(data=True):
        print(f"  {edge[0]} -> {edge[1]}: {edge[2]['distance_km']} km")
