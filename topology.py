"""
Módulo de topología para el simulador EON
Implementa la creación de la red NSFNET con distancias realistas
"""

import networkx as nx
from config import NSFNET_NODES, NSFNET_LINKS


def create_nsfnet():
    """
    Crea la topología NSFNET REAL con 14 nodos y 23 enlaces bidireccionales
    Incluye distancias reales en kilómetros de la topología oficial
    
    Returns:
        networkx.Graph: Grafo no dirigido de la red NSFNET con atributos de distancia
    """
    # Crear grafo NO dirigido para NSFNET (enlaces bidireccionales por naturaleza)
    G = nx.Graph()
    
    # Agregar nodos (numerados del 0 al 13)
    for i in range(NSFNET_NODES):
        G.add_node(i)
    
    # Definir enlaces de NSFNET con distancias REALES de la topología oficial (en km)
    # Topología NSFNET real con 23 enlaces únicos bidireccionales
    # Nodos: 0=Nodo1, 1=Nodo2, 2=Nodo3, 3=Nodo4, 4=Nodo5, 5=Nodo6, 6=Nodo7, 7=Nodo8, 8=Nodo9, 9=Nodo10, 10=Nodo11, 11=Nodo12, 12=Nodo13, 13=Nodo14
    nsfnet_links = [
        # 23 enlaces de la topología real NSFNET (según imagen oficial)
        (0, 1, 2100),   # 1-2
        (0, 2, 3000),   # 1-3
        (0, 6, 4800),   # 1-7
        (1, 2, 1200),   # 2-3
        (1, 3, 1500),   # 2-4
        (2, 5, 3600),   # 3-6
        (3, 4, 1200),   # 4-5
        (3, 6, 3900),   # 4-7
        (4, 5, 2400),   # 5-6
        (4, 6, 1200),   # 5-7
        (5, 6, 2700),   # 6-7
        (5, 9, 2100),   # 6-10
        (5, 8, 3600),   # 6-9
        (6, 7, 1500),   # 7-8
        (7, 8, 1500),   # 8-9
        (7, 10, 1500),  # 8-11
        (8, 9, 1500),   # 9-10
        (8, 11, 600),   # 9-12
        (8, 12, 600),   # 9-13
        (8, 13, 600),   # 9-14
        (10, 11, 1200), # 11-12
        (11, 12, 600),  # 12-13
        (12, 13, 300),  # 13-14
    ]
    
    # Agregar enlaces al grafo (en Graph son automáticamente bidireccionales)
    for source, target, distance in nsfnet_links:
        G.add_edge(source, target, distance_km=distance)
    
    # Verificar que tenemos el número correcto de enlaces
    actual_links = G.number_of_edges()
    if actual_links != NSFNET_LINKS:
        print(f"Advertencia: NSFNET tiene {actual_links} enlaces, esperados {NSFNET_LINKS} enlaces bidireccionales")
    
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
        'is_connected': nx.is_connected(G),  # Para grafos no dirigidos
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
