"""
Simulador principal para Redes Ópticas Elásticas (EONs)
Ejecuta experimentos comparativos entre algoritmos SPFF y k-SP-MW
"""

import matplotlib.pyplot as plt
import numpy as np
import time
from typing import List, Dict, Tuple

from config import DEMAND_LOADS, RUNS_PER_LOAD
from topology import create_nsfnet
from network_model import NetworkState
from algorithms import run_spff, run_ksp_mw
from utils import generate_demands


class EONSimulator:
    """
    Clase principal del simulador EON
    """
    
    def __init__(self):
        """
        Inicializa el simulador
        """
        self.graph = create_nsfnet()
        self.results = {
            'loads': [],
            'spff_watermarks': [],
            'ksp_watermarks': [],
            'spff_blocking': [],
            'ksp_blocking': [],
            'spff_utilization': [],
            'ksp_utilization': []
        }
        
        print("Simulador EON inicializado")
        print(f"Red NSFNET: {self.graph.number_of_nodes()} nodos, {self.graph.number_of_edges()} enlaces")
    
    def run_single_experiment(self, num_demands: int, seed: int) -> Dict:
        """
        Ejecuta un experimento individual con un número específico de demandas
        
        Args:
            num_demands (int): Número de demandas a generar
            seed (int): Semilla para reproducibilidad
            
        Returns:
            dict: Resultados del experimento
        """
        # Generar demandas
        demands = generate_demands(self.graph, num_demands, seed=seed)
        
        # Crear estados de red independientes para cada algoritmo
        network_spff = NetworkState(self.graph)
        network_ksp = NetworkState(self.graph)
        
        # Ejecutar SPFF
        spff_results = run_spff(self.graph, demands, network_spff)
        
        # Ejecutar k-SP-MW
        ksp_results = run_ksp_mw(self.graph, demands, network_ksp)
        
        return {
            'spff': spff_results,
            'ksp_mw': ksp_results,
            'num_demands': num_demands,
            'seed': seed
        }
    
    def run_experiments(self):
        """
        Ejecuta todos los experimentos para diferentes cargas de demanda
        """
        print("\nIniciando experimentos...")
        print(f"Cargas de demanda: {DEMAND_LOADS}")
        print(f"Ejecuciones por carga: {RUNS_PER_LOAD}")
        
        total_experiments = len(DEMAND_LOADS) * RUNS_PER_LOAD
        current_experiment = 0
        
        for load in DEMAND_LOADS:
            print(f"\nProcesando carga: {load} demandas")
            
            spff_watermarks = []
            ksp_watermarks = []
            spff_blocking = []
            ksp_blocking = []
            spff_utilization = []
            ksp_utilization = []
            
            for run in range(RUNS_PER_LOAD):
                current_experiment += 1
                progress = (current_experiment / total_experiments) * 100
                
                # Ejecutar experimento individual
                experiment_results = self.run_single_experiment(load, seed=run)
                
                # Recopilar resultados
                spff_watermarks.append(experiment_results['spff']['watermark'])
                ksp_watermarks.append(experiment_results['ksp_mw']['watermark'])
                spff_blocking.append(experiment_results['spff']['blocking_probability'])
                ksp_blocking.append(experiment_results['ksp_mw']['blocking_probability'])
                spff_utilization.append(experiment_results['spff']['utilization'])
                ksp_utilization.append(experiment_results['ksp_mw']['utilization'])
                
                if (run + 1) % 10 == 0:
                    print(f"  Completado: {run + 1}/{RUNS_PER_LOAD} ejecuciones ({progress:.1f}%)")
            
            # Calcular promedios
            avg_spff_watermark = np.mean(spff_watermarks)
            avg_ksp_watermark = np.mean(ksp_watermarks)
            avg_spff_blocking = np.mean(spff_blocking)
            avg_ksp_blocking = np.mean(ksp_blocking)
            avg_spff_utilization = np.mean(spff_utilization)
            avg_ksp_utilization = np.mean(ksp_utilization)
            
            # Almacenar resultados
            self.results['loads'].append(load)
            self.results['spff_watermarks'].append(avg_spff_watermark)
            self.results['ksp_watermarks'].append(avg_ksp_watermark)
            self.results['spff_blocking'].append(avg_spff_blocking)
            self.results['ksp_blocking'].append(avg_ksp_blocking)
            self.results['spff_utilization'].append(avg_spff_utilization)
            self.results['ksp_utilization'].append(avg_ksp_utilization)
            
            print(f"  Promedio SPFF - Watermark: {avg_spff_watermark:.2f}, Bloqueo: {avg_spff_blocking:.3f}")
            print(f"  Promedio k-SP-MW - Watermark: {avg_ksp_watermark:.2f}, Bloqueo: {avg_ksp_blocking:.3f}")
            print(f"  Mejora en watermark: {avg_spff_watermark - avg_ksp_watermark:.2f}")
    
    def generate_plots(self):
        """
        Genera gráficos de los resultados
        """
        print("\nGenerando gráficos...")
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8')
        
        # Crear figura con dos subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico 1: Carga vs Watermark
        ax1.plot(self.results['loads'], self.results['spff_watermarks'], 
                'o-', label='SPFF', linewidth=2, markersize=8)
        ax1.plot(self.results['loads'], self.results['ksp_watermarks'], 
                's-', label='k-SP-MW', linewidth=2, markersize=8)
        
        ax1.set_xlabel('Carga de Demanda', fontsize=12)
        ax1.set_ylabel('Watermark Promedio', fontsize=12)
        ax1.set_title('Comparación de Watermark: SPFF vs k-SP-MW', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(self.results['loads'])
        
        # Gráfico 2: Carga vs Probabilidad de Bloqueo
        ax2.plot(self.results['loads'], self.results['spff_blocking'], 
                'o-', label='SPFF', linewidth=2, markersize=8)
        ax2.plot(self.results['loads'], self.results['ksp_blocking'], 
                's-', label='k-SP-MW', linewidth=2, markersize=8)
        
        ax2.set_xlabel('Carga de Demanda', fontsize=12)
        ax2.set_ylabel('Probabilidad de Bloqueo Promedio', fontsize=12)
        ax2.set_title('Comparación de Probabilidad de Bloqueo: SPFF vs k-SP-MW', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(self.results['loads'])
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('eon_simulation_results.png', dpi=300, bbox_inches='tight')
        print("Gráfico guardado como: eon_simulation_results.png")
        
        # Mostrar gráfico
        plt.show()
    
    def print_summary(self):
        """
        Imprime un resumen de los resultados
        """
        print("\n" + "="*60)
        print("RESUMEN DE RESULTADOS")
        print("="*60)
        
        print(f"{'Carga':<8} {'SPFF WM':<10} {'k-SP WM':<10} {'Mejora WM':<12} {'SPFF Bl':<10} {'k-SP Bl':<10}")
        print("-" * 60)
        
        for i, load in enumerate(self.results['loads']):
            spff_wm = self.results['spff_watermarks'][i]
            ksp_wm = self.results['ksp_watermarks'][i]
            improvement = spff_wm - ksp_wm
            spff_bl = self.results['spff_blocking'][i]
            ksp_bl = self.results['ksp_blocking'][i]
            
            print(f"{load:<8} {spff_wm:<10.2f} {ksp_wm:<10.2f} {improvement:<12.2f} {spff_bl:<10.3f} {ksp_bl:<10.3f}")
        
        # Calcular mejoras promedio
        avg_watermark_improvement = np.mean([spff - ksp for spff, ksp in 
                                           zip(self.results['spff_watermarks'], 
                                               self.results['ksp_watermarks'])])
        avg_blocking_improvement = np.mean([spff - ksp for spff, ksp in 
                                          zip(self.results['spff_blocking'], 
                                              self.results['ksp_blocking'])])
        
        print("-" * 60)
        print(f"Mejora promedio en watermark: {avg_watermark_improvement:.2f}")
        print(f"Mejora promedio en bloqueo: {avg_blocking_improvement:.3f}")
        
        # Calcular eficiencia espectral
        print("\nEficiencia espectral promedio:")
        for i, load in enumerate(self.results['loads']):
            spff_eff = load / self.results['spff_watermarks'][i] if self.results['spff_watermarks'][i] > 0 else 0
            ksp_eff = load / self.results['ksp_watermarks'][i] if self.results['ksp_watermarks'][i] > 0 else 0
            print(f"  Carga {load}: SPFF={spff_eff:.3f}, k-SP-MW={ksp_eff:.3f}")
    
    def save_results(self, filename: str = 'simulation_results.txt'):
        """
        Guarda los resultados en un archivo de texto
        
        Args:
            filename (str): Nombre del archivo de salida
        """
        with open(filename, 'w') as f:
            f.write("Resultados de Simulación EON\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Cargas de demanda: {DEMAND_LOADS}\n")
            f.write(f"Ejecuciones por carga: {RUNS_PER_LOAD}\n\n")
            
            f.write("Resultados detallados:\n")
            f.write("-"*50 + "\n")
            
            for i, load in enumerate(self.results['loads']):
                f.write(f"Carga: {load}\n")
                f.write(f"  SPFF - Watermark: {self.results['spff_watermarks'][i]:.2f}, "
                       f"Bloqueo: {self.results['spff_blocking'][i]:.3f}\n")
                f.write(f"  k-SP-MW - Watermark: {self.results['ksp_watermarks'][i]:.2f}, "
                       f"Bloqueo: {self.results['ksp_blocking'][i]:.3f}\n")
                f.write(f"  Mejora en watermark: {self.results['spff_watermarks'][i] - self.results['ksp_watermarks'][i]:.2f}\n\n")
        
        print(f"Resultados guardados en: {filename}")


def main():
    """
    Función principal del simulador
    """
    print("Simulador de Redes Ópticas Elásticas (EONs)")
    print("Algoritmos: SPFF vs k-SP-MW")
    print("Objetivo: Minimizar watermark del espectro")
    print("-" * 50)
    
    # Crear y ejecutar simulador
    simulator = EONSimulator()
    
    start_time = time.time()
    simulator.run_experiments()
    end_time = time.time()
    
    # Generar resultados
    simulator.print_summary()
    simulator.generate_plots()
    simulator.save_results()
    
    print(f"\nSimulación completada en {end_time - start_time:.2f} segundos")


if __name__ == "__main__":
    main()
