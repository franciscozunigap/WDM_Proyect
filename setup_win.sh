#!/bin/bash

echo "==============================================="
echo "Configurando el entorno para el simulador EON..."
echo "==============================================="

# Crear entorno virtual
echo "Creando entorno virtual..."
python -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/Scripts/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ ¡Configuración completada!"
echo ""
echo "Para activar el entorno virtual en el futuro, ejecuta:"
echo "  source venv/Scripts/activate"
echo ""
echo "Para ejecutar la simulación:"
echo "  python main.py"
echo ""
