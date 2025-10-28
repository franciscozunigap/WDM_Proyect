#!/bin/bash

# Script de configuración para el simulador de Redes Ópticas Elásticas (EONs)
# Proyecto RMLSA - Routing, Modulation, and Spectrum Assignment

echo "Configurando el entorno para el simulador EON..."

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "¡Configuración completada!"
echo ""
echo "Para activar el entorno virtual en el futuro, ejecuta:"
echo "source venv/bin/activate"
echo ""
echo "Para ejecutar la simulación:"
echo "python main.py"
