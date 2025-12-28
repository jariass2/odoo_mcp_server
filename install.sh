#!/bin/bash

# Script de instalación rápida de Odoo MCP Server
# Uso: bash install.sh

set -e

echo "================================================"
echo "  Instalación de Odoo MCP Server para Claude"
echo "================================================"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker detectado: $(docker --version)"
echo "✅ Docker Compose detectado: $(docker-compose --version)"
echo ""

# Verificar archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "Creando desde .env.example..."
    cp .env.example .env
    echo ""
    echo "🔧 IMPORTANTE: Edita el archivo .env con tus credenciales de Odoo"
    echo "   nano .env"
    echo ""
    read -p "¿Has configurado el archivo .env? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Por favor configura .env y vuelve a ejecutar este script"
        exit 1
    fi
fi

echo "📦 Construyendo imagen Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando contenedor..."
docker-compose up -d

echo ""
echo "⏳ Esperando que el servicio esté listo..."
sleep 10

echo ""
echo "🏥 Verificando health check..."
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Servidor MCP funcionando correctamente!"
    echo ""
    echo "📊 Endpoints disponibles:"
    echo "   - Health: http://localhost:8000/health"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - Tools: http://localhost:8000/tools"
    echo ""
    echo "📝 Ver logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🎉 ¡Instalación completada!"
else
    echo "⚠️  El servidor no responde en http://localhost:8000/health"
    echo ""
    echo "Ver logs para diagnosticar:"
    echo "   docker-compose logs"
    echo ""
    echo "Verificar estado:"
    echo "   docker-compose ps"
fi

echo ""
echo "================================================"
