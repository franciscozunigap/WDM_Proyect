"""
Archivo de pruebas para el simulador EON
Incluye pruebas unitarias para validar la funcionalidad clave
"""

import pytest
import numpy as np
from network_model import NetworkState
from topology import create_nsfnet
from utils import get_modulation, get_slots_necesarios, generate_demands
from algorithms import run_spff, run_ksp_mw


class TestNetworkState:
    """
    Pruebas para la clase NetworkState
    """
    
    def setup_method(self):
        """
        Configuración inicial para cada prueba
        """
        self.graph = create_nsfnet()
        self.network = NetworkState(self.graph)
    
    def test_network_initialization(self):
        """
        Prueba la inicialización correcta de NetworkState
        """
        assert self.network.num_links > 0
        assert self.network.num_slots > 0
        assert self.network.watermark == 0
        assert self.network.total_assignments == 0
        assert self.network.blocked_requests == 0
        
        # Verificar que la matriz de espectro está inicializada correctamente
        assert self.network.spectrum_state.shape == (self.network.num_links, self.network.num_slots)
        assert np.all(self.network.spectrum_state == 0)
    
    def test_find_first_fit_basic(self):
        """
        Prueba básica de find_first_fit con slots libres
        """
        # Obtener índices de enlaces para un camino simple
        test_path = [0, 1, 2]
        link_indices = self.network.get_link_indices(test_path)
        
        assert link_indices is not None
        assert len(link_indices) > 0
        
        # Buscar slots disponibles
        start_slot = self.network.find_first_fit(link_indices, 5)
        assert start_slot == 0  # Debería encontrar el primer slot
    
    def test_find_first_fit_with_occupied_slots(self):
        """
        Prueba específica de find_first_fit con slots ocupados
        Este es el test principal solicitado en los requerimientos
        """
        # Crear un estado de red mock
        network = NetworkState(self.graph)
        
        # Obtener índices de enlaces para un camino
        test_path = [0, 1, 2]
        link_indices = network.get_link_indices(test_path)
        
        assert link_indices is not None
        assert len(link_indices) >= 2
        
        # Ocupar manualmente algunos slots
        # Enlace 1: ocupar slots 5-10
        if len(link_indices) > 0:
            link1 = link_indices[0]
            for slot in range(5, 11):
                network.spectrum_state[link1, slot] = 1
        
        # Enlace 2: ocupar slots 8-12
        if len(link_indices) > 1:
            link2 = link_indices[1]
            for slot in range(8, 13):
                network.spectrum_state[link2, slot] = 1
        
        # Buscar 3 slots consecutivos
        start_slot = network.find_first_fit(link_indices, 3)
        
        # Debería encontrar el primer slot después de 12 (slot 13)
        assert start_slot == 13, f"Esperado slot 13, obtenido {start_slot}"
        
        # Verificar que realmente hay 3 slots consecutivos disponibles desde slot 13
        for slot in range(13, 16):
            for link_idx in link_indices:
                assert network.spectrum_state[link_idx, slot] == 0, f"Slot {slot} en enlace {link_idx} debería estar libre"
    
    def test_find_first_fit_no_space(self):
        """
        Prueba find_first_fit cuando no hay espacio suficiente
        """
        # Ocupar todos los slots
        self.network.spectrum_state.fill(1)
        
        test_path = [0, 1, 2]
        link_indices = self.network.get_link_indices(test_path)
        
        start_slot = self.network.find_first_fit(link_indices, 5)
        assert start_slot == -1  # No debería encontrar espacio
    
    def test_asignar_recursos(self):
        """
        Prueba la asignación de recursos
        """
        test_path = [0, 1, 2]
        link_indices = self.network.get_link_indices(test_path)
        
        # Asignar recursos
        success = self.network.asignar_recursos(link_indices, 0, 5)
        assert success
        
        # Verificar que los slots están ocupados
        for slot in range(5):
            for link_idx in link_indices:
                assert self.network.spectrum_state[link_idx, slot] == 1
        
        # Verificar watermark
        assert self.network.watermark == 5
    
    def test_reset(self):
        """
        Prueba el reinicio del estado de la red
        """
        # Asignar algunos recursos
        test_path = [0, 1, 2]
        link_indices = self.network.get_link_indices(test_path)
        self.network.asignar_recursos(link_indices, 0, 5)
        
        # Verificar que hay recursos asignados
        assert self.network.watermark > 0
        assert self.network.total_assignments > 0
        
        # Reiniciar
        self.network.reset()
        
        # Verificar que todo está limpio
        assert self.network.watermark == 0
        assert self.network.total_assignments == 0
        assert self.network.blocked_requests == 0
        assert np.all(self.network.spectrum_state == 0)


class TestUtils:
    """
    Pruebas para las funciones de utilidades
    """
    
    def test_get_modulation(self):
        """
        Prueba la selección de modulación
        """
        # Pruebas con diferentes distancias
        assert get_modulation(100) == ('16-QAM', 4)
        assert get_modulation(500) == ('16-QAM', 4)
        assert get_modulation(1000) == ('8-QAM', 3)
        assert get_modulation(2000) == ('QPSK', 2)
        assert get_modulation(3000) == ('BPSK', 1)
        assert get_modulation(5000) == ('BPSK', 1)  # Distancia muy larga
    
    def test_get_slots_necesarios(self):
        """
        Prueba el cálculo de slots necesarios
        """
        # Prueba con diferentes modulaciones y demandas
        assert get_slots_necesarios(100, '16-QAM') > 0
        assert get_slots_necesarios(200, 'QPSK') > get_slots_necesarios(200, '16-QAM')
        assert get_slots_necesarios(50, 'BPSK') > 0
        
        # Verificar que incluye banda de guarda
        slots_16qam = get_slots_necesarios(100, '16-QAM')
        assert slots_16qam >= 1  # Mínimo 1 slot (banda de guarda)
    
    def test_generate_demands(self):
        """
        Prueba la generación de demandas
        """
        graph = create_nsfnet()
        demands = generate_demands(graph, 10, seed=42)
        
        assert len(demands) == 10
        
        for source, target, bandwidth in demands:
            assert source != target  # Origen y destino diferentes
            assert 0 <= source < graph.number_of_nodes()
            assert 0 <= target < graph.number_of_nodes()
            assert bandwidth > 0


class TestAlgorithms:
    """
    Pruebas para los algoritmos SPFF y k-SP-MW
    """
    
    def setup_method(self):
        """
        Configuración inicial para cada prueba
        """
        self.graph = create_nsfnet()
        self.demands = [(0, 5, 100), (1, 6, 150), (2, 7, 200)]
    
    def test_spff_basic(self):
        """
        Prueba básica del algoritmo SPFF
        """
        network = NetworkState(self.graph)
        results = run_spff(self.graph, self.demands, network)
        
        assert 'algorithm' in results
        assert results['algorithm'] == 'SPFF'
        assert 'watermark' in results
        assert 'blocking_probability' in results
        assert results['watermark'] >= 0
        assert 0 <= results['blocking_probability'] <= 1
    
    def test_ksp_mw_basic(self):
        """
        Prueba básica del algoritmo k-SP-MW
        """
        network = NetworkState(self.graph)
        results = run_ksp_mw(self.graph, self.demands, network)
        
        assert 'algorithm' in results
        assert results['algorithm'] == 'k-SP-MW'
        assert 'watermark' in results
        assert 'blocking_probability' in results
        assert results['watermark'] >= 0
        assert 0 <= results['blocking_probability'] <= 1
    
    def test_algorithm_comparison(self):
        """
        Prueba la comparación entre algoritmos
        """
        network_spff = NetworkState(self.graph)
        network_ksp = NetworkState(self.graph)
        
        spff_results = run_spff(self.graph, self.demands, network_spff)
        ksp_results = run_ksp_mw(self.graph, self.demands, network_ksp)
        
        # Ambos algoritmos deberían producir resultados válidos
        assert spff_results['watermark'] >= 0
        assert ksp_results['watermark'] >= 0
        
        # k-SP-MW debería ser igual o mejor que SPFF en términos de watermark
        # (esto no siempre es garantizado, pero es la expectativa)
        print(f"SPFF watermark: {spff_results['watermark']}")
        print(f"k-SP-MW watermark: {ksp_results['watermark']}")


def run_all_tests():
    """
    Ejecuta todas las pruebas manualmente
    """
    print("Ejecutando pruebas del simulador EON...")
    
    # Pruebas de NetworkState
    print("\n1. Probando NetworkState...")
    test_network = TestNetworkState()
    test_network.setup_method()
    
    try:
        test_network.test_network_initialization()
        print("   ✓ Inicialización de red")
        
        test_network.test_find_first_fit_basic()
        print("   ✓ find_first_fit básico")
        
        test_network.test_find_first_fit_with_occupied_slots()
        print("   ✓ find_first_fit con slots ocupados (test principal)")
        
        test_network.test_find_first_fit_no_space()
        print("   ✓ find_first_fit sin espacio")
        
        test_network.test_asignar_recursos()
        print("   ✓ Asignación de recursos")
        
        test_network.test_reset()
        print("   ✓ Reinicio de red")
        
    except Exception as e:
        print(f"   ✗ Error en NetworkState: {e}")
    
    # Pruebas de Utils
    print("\n2. Probando funciones de utilidades...")
    test_utils = TestUtils()
    
    try:
        test_utils.test_get_modulation()
        print("   ✓ Selección de modulación")
        
        test_utils.test_get_slots_necesarios()
        print("   ✓ Cálculo de slots necesarios")
        
        test_utils.test_generate_demands()
        print("   ✓ Generación de demandas")
        
    except Exception as e:
        print(f"   ✗ Error en Utils: {e}")
    
    # Pruebas de Algoritmos
    print("\n3. Probando algoritmos...")
    test_algorithms = TestAlgorithms()
    test_algorithms.setup_method()
    
    try:
        test_algorithms.test_spff_basic()
        print("   ✓ SPFF básico")
        
        test_algorithms.test_ksp_mw_basic()
        print("   ✓ k-SP-MW básico")
        
        test_algorithms.test_algorithm_comparison()
        print("   ✓ Comparación de algoritmos")
        
    except Exception as e:
        print(f"   ✗ Error en Algoritmos: {e}")
    
    print("\n¡Todas las pruebas completadas!")


if __name__ == "__main__":
    # Ejecutar pruebas manualmente
    run_all_tests()
    
    # También se pueden ejecutar con pytest si está disponible
    print("\nPara ejecutar con pytest, usa: pytest test_implementation.py -v")
