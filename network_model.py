"""
Modelo de red para el simulador EON
Implementa la clase NetworkState que maneja el estado del espectro en la red
"""

import numpy as np
import networkx as nx
from config import MAX_SLOTS


class NetworkState:
    """
    Clase que representa el estado del espectro en la red EON
    Maneja la asignación de slots y el cálculo del watermark
    """
    
    def __init__(self, graph):
        """
        Inicializa el estado de la red
        
        Args:
            graph (networkx.Graph): Grafo de la red
        """
        self.graph = graph
        self.num_links = graph.number_of_edges()
        self.num_slots = MAX_SLOTS
        
        # Crear mapeo de enlaces a índices
        self.link_to_index = {}
        self.index_to_link = {}
        
        # Mapear cada enlace a un índice único
        for i, (source, target) in enumerate(graph.edges()):
            self.link_to_index[(source, target)] = i
            self.index_to_link[i] = (source, target)
        
        # Estado del espectro: matriz de enlaces x slots
        # 0 = libre, 1 = ocupado
        self.spectrum_state = np.zeros((self.num_links, self.num_slots), dtype=int)
        
        # Watermark global (slot más alto ocupado en toda la red)
        self.watermark = 0
        
        # Estadísticas
        self.total_assignments = 0
        self.blocked_requests = 0
    
    def reset(self):
        """
        Reinicia el estado de la red para una nueva ejecución
        """
        self.spectrum_state.fill(0)
        self.watermark = 0
        self.total_assignments = 0
        self.blocked_requests = 0
    
    def get_link_indices(self, path):
        """
        Obtiene los índices de los enlaces que forman un camino
        
        Args:
            path (list): Lista de nodos que forman el camino
            
        Returns:
            list: Lista de índices de enlaces
        """
        link_indices = []
        
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Buscar enlace en ambas direcciones
            if (source, target) in self.link_to_index:
                link_indices.append(self.link_to_index[(source, target)])
            elif (target, source) in self.link_to_index:
                link_indices.append(self.link_to_index[(target, source)])
            else:
                # Enlace no encontrado
                return None
        
        return link_indices
    
    def find_first_fit(self, link_indices, slots_needed):
        """
        Encuentra el primer slot disponible común a todos los enlaces del camino
        
        Args:
            link_indices (list): Lista de índices de enlaces
            slots_needed (int): Número de slots consecutivos necesarios
            
        Returns:
            int: Índice del primer slot disponible, o -1 si no hay espacio
        """
        if not link_indices or slots_needed <= 0:
            return -1
        
        # Verificar que todos los enlaces existen
        for link_idx in link_indices:
            if link_idx >= self.num_links or link_idx < 0:
                return -1
        
        # Buscar el primer slot disponible
        for start_slot in range(self.num_slots - slots_needed + 1):
            # Verificar si hay slots consecutivos disponibles en todos los enlaces
            available = True
            
            for slot in range(start_slot, start_slot + slots_needed):
                for link_idx in link_indices:
                    if self.spectrum_state[link_idx, slot] == 1:
                        available = False
                        break
                if not available:
                    break
            
            if available:
                return start_slot
        
        return -1  # No hay espacio disponible
    
    def find_best_fit_positions(self, link_indices, slots_needed, max_positions=10):
        """
        Encuentra múltiples posiciones candidatas de slot que minimizan el watermark
        
        Estrategias consideradas:
        1. Posiciones que no aumentan el watermark de ningún enlace
        2. Posiciones que minimizan el aumento del watermark máximo
        3. Posiciones que minimizan fragmentación
        
        Args:
            link_indices (list): Lista de índices de enlaces
            slots_needed (int): Número de slots consecutivos necesarios
            max_positions (int): Máximo número de posiciones a retornar
            
        Returns:
            list: Lista de posiciones de inicio ordenadas por conveniencia
        """
        if not link_indices or slots_needed <= 0:
            return []
        
        # Verificar que todos los enlaces existen
        for link_idx in link_indices:
            if link_idx >= self.num_links or link_idx < 0:
                return []
        
        # Calcular watermarks actuales de los enlaces del camino
        current_watermarks = [self.get_link_watermark(link_idx) for link_idx in link_indices]
        max_current_watermark = max(current_watermarks) if current_watermarks else 0
        
        candidate_positions = []
        positions_no_increase = []  # Posiciones que no aumentan el watermark
        
        # Buscar todas las posiciones disponibles y calcular su "score"
        for start_slot in range(self.num_slots - slots_needed + 1):
            # Verificar si hay slots consecutivos disponibles en todos los enlaces
            available = True
            
            for slot in range(start_slot, start_slot + slots_needed):
                for link_idx in link_indices:
                    if self.spectrum_state[link_idx, slot] == 1:
                        available = False
                        break
                if not available:
                    break
            
            if available:
                # Calcular watermark máximo que resultaría
                end_slot = start_slot + slots_needed
                max_new_watermark = max(max_current_watermark, end_slot)
                
                # Calcular cuánto aumenta el watermark
                watermark_increase = max_new_watermark - max_current_watermark
                
                # Priorizar posiciones que no aumentan el watermark
                if watermark_increase == 0:
                    # Score basado solo en fragmentación y posición
                    score = start_slot * 0.1
                    positions_no_increase.append((start_slot, score))
                else:
                    # Score que penaliza aumentos de watermark
                    score = watermark_increase * 10000 + max_new_watermark * 100 + start_slot * 0.1
                    candidate_positions.append((start_slot, score))
        
        # Priorizar posiciones que no aumentan el watermark
        if positions_no_increase:
            positions_no_increase.sort(key=lambda x: x[1])
            result = [pos for pos, score in positions_no_increase[:max_positions]]
            
            # Si no hay suficientes, agregar algunas que sí aumentan
            if len(result) < max_positions and candidate_positions:
                candidate_positions.sort(key=lambda x: x[1])
                remaining = max_positions - len(result)
                result.extend([pos for pos, score in candidate_positions[:remaining]])
            
            return result
        
        # Si todas aumentan el watermark, retornar las que menos lo aumentan
        if not candidate_positions:
            return []
        
        candidate_positions.sort(key=lambda x: x[1])
        return [pos for pos, score in candidate_positions[:max_positions]]
    
    def get_link_watermark(self, link_idx):
        """
        Obtiene el watermark de un enlace específico
        
        Args:
            link_idx (int): Índice del enlace
            
        Returns:
            int: Watermark del enlace (slot más alto ocupado + 1)
        """
        if link_idx >= self.num_links or link_idx < 0:
            return 0
        
        # Encontrar el último slot ocupado en este enlace
        for slot in range(self.num_slots - 1, -1, -1):
            if self.spectrum_state[link_idx, slot] == 1:
                return slot + 1
        
        return 0  # No hay slots ocupados
    
    def asignar_recursos(self, link_indices, start_slot, slots_needed):
        """
        Asigna recursos del espectro marcando los slots como ocupados
        
        Args:
            link_indices (list): Lista de índices de enlaces
            start_slot (int): Slot inicial para la asignación
            slots_needed (int): Número de slots a asignar
            
        Returns:
            bool: True si la asignación fue exitosa
        """
        if not link_indices or slots_needed <= 0:
            return False
        
        # Verificar que la asignación es válida
        if start_slot < 0 or start_slot + slots_needed > self.num_slots:
            return False
        
        # Verificar que todos los slots están libres
        for slot in range(start_slot, start_slot + slots_needed):
            for link_idx in link_indices:
                if self.spectrum_state[link_idx, slot] == 1:
                    return False  # Slot ya ocupado
        
        # Realizar la asignación
        for slot in range(start_slot, start_slot + slots_needed):
            for link_idx in link_indices:
                self.spectrum_state[link_idx, slot] = 1
        
        # Actualizar watermark
        end_slot = start_slot + slots_needed - 1
        self.watermark = max(self.watermark, end_slot + 1)
        
        # Actualizar estadísticas
        self.total_assignments += 1
        
        return True
    
    def liberar_recursos(self, link_indices, start_slot, slots_needed):
        """
        Libera recursos del espectro marcando los slots como libres
        
        Args:
            link_indices (list): Lista de índices de enlaces
            start_slot (int): Slot inicial para liberar
            slots_needed (int): Número de slots a liberar
        """
        if not link_indices or slots_needed <= 0:
            return
        
        # Liberar slots
        for slot in range(start_slot, start_slot + slots_needed):
            for link_idx in link_indices:
                if link_idx < self.num_links:
                    self.spectrum_state[link_idx, slot] = 0
        
        # Recalcular watermark
        self._recalculate_watermark()
    
    def _recalculate_watermark(self):
        """
        Recalcula el watermark global después de liberar recursos
        """
        self.watermark = 0
        
        for link_idx in range(self.num_links):
            # Encontrar el último slot ocupado en este enlace
            for slot in range(self.num_slots - 1, -1, -1):
                if self.spectrum_state[link_idx, slot] == 1:
                    self.watermark = max(self.watermark, slot + 1)
                    break
    
    def get_watermark(self):
        """
        Obtiene el watermark actual de la red
        
        Returns:
            int: Watermark actual
        """
        return self.watermark
    
    def get_utilization(self):
        """
        Calcula la utilización promedio del espectro
        
        Returns:
            float: Utilización promedio (0.0 a 1.0)
        """
        total_slots = self.num_links * self.num_slots
        occupied_slots = np.sum(self.spectrum_state)
        
        return occupied_slots / total_slots if total_slots > 0 else 0.0
    
    def get_link_utilization(self, link_idx):
        """
        Calcula la utilización de un enlace específico
        
        Args:
            link_idx (int): Índice del enlace
            
        Returns:
            float: Utilización del enlace (0.0 a 1.0)
        """
        if link_idx >= self.num_links or link_idx < 0:
            return 0.0
        
        occupied_slots = np.sum(self.spectrum_state[link_idx, :])
        return occupied_slots / self.num_slots
    
    def get_statistics(self):
        """
        Obtiene estadísticas del estado actual de la red
        
        Returns:
            dict: Diccionario con estadísticas
        """
        return {
            'watermark': self.watermark,
            'utilization': self.get_utilization(),
            'total_assignments': self.total_assignments,
            'blocked_requests': self.blocked_requests,
            'blocking_probability': self.blocked_requests / (self.total_assignments + self.blocked_requests) if (self.total_assignments + self.blocked_requests) > 0 else 0.0
        }
    
    def print_state(self):
        """
        Imprime el estado actual de la red (para debugging)
        """
        print(f"Watermark: {self.watermark}")
        print(f"Utilización: {self.get_utilization():.3f}")
        print(f"Asignaciones totales: {self.total_assignments}")
        print(f"Solicitudes bloqueadas: {self.blocked_requests}")
        
        # Mostrar estado de los primeros 10 slots de cada enlace
        print("\nEstado del espectro (primeros 10 slots):")
        for link_idx in range(min(5, self.num_links)):  # Solo primeros 5 enlaces
            link = self.index_to_link[link_idx]
            state_str = ''.join(['1' if self.spectrum_state[link_idx, i] == 1 else '0' 
                               for i in range(min(10, self.num_slots))])
            print(f"Enlace {link}: {state_str}")


if __name__ == "__main__":
    # Prueba básica del módulo
    from topology import create_nsfnet
    
    G = create_nsfnet()
    network = NetworkState(G)
    
    print("Prueba básica de NetworkState:")
    print(f"Número de enlaces: {network.num_links}")
    print(f"Número de slots: {network.num_slots}")
    
    # Probar asignación de recursos
    test_path = [0, 1, 2]  # Camino de prueba
    link_indices = network.get_link_indices(test_path)
    
    if link_indices:
        print(f"Índices de enlaces para camino {test_path}: {link_indices}")
        
        # Buscar slots disponibles
        start_slot = network.find_first_fit(link_indices, 5)
        print(f"Primer slot disponible para 5 slots: {start_slot}")
        
        if start_slot >= 0:
            # Asignar recursos
            success = network.asignar_recursos(link_indices, start_slot, 5)
            print(f"Asignación exitosa: {success}")
            print(f"Watermark después de asignación: {network.get_watermark()}")
            
            # Mostrar estadísticas
            stats = network.get_statistics()
            print(f"Estadísticas: {stats}")
    
    network.print_state()
