# Odoo MCP Server for Claude

🤖 **Servidor MCP (Model Context Protocol) para integrar Odoo con Claude AI**

Este servidor expone herramientas de análisis de ventas, clientes y CRM de Odoo para que Claude pueda acceder y analizar datos empresariales en tiempo real.

## 📋 Características

### Herramientas Disponibles

1. **📊 Sales Data** - Obtener datos de ventas con filtros avanzados
2. **👥 Customer Insights** - Análisis RFM y segmentación de clientes (VIP, At Risk, New, etc.)
3. **🎯 CRM Opportunities** - Análisis del pipeline de ventas
4. **📦 Product Performance** - Rendimiento y ranking de productos
5. **👨‍💼 Sales Team Performance** - Métricas del equipo comercial
6. **🔍 Customer Search** - Búsqueda rápida de clientes
7. **📈 Comprehensive Data** - Análisis completo en una sola llamada

### Segmentación de Clientes (RFM)

El servidor implementa análisis RFM automático:
- **VIP**: Alta facturación (>€10k) y frecuencia (>5 compras)
- **At Risk**: Clientes recurrentes sin compras en 180+ días
- **New**: Primera compra en los últimos 30 días
- **Inactive**: Sin compras en más de 365 días
- **Regular**: Resto de clientes activos

## 🚀 Instalación y Configuración

### Requisitos Previos

- Docker y Docker Compose instalados
- Acceso a una instancia de Odoo (v14+)
- API Key de Odoo (generar en: Preferencias > Seguridad > API Keys)

### Paso 1: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Contenido del archivo `.env`:**

```bash
ODOO_URL=http://tu-instancia.odoo.com/
ODOO_DB=tu-database-name
ODOO_USERNAME=integracion@tuempresa.com
ODOO_API_KEY=tu-api-key-de-odoo
```

### Paso 2: Construir y Ejecutar

```bash
# Construir la imagen Docker
docker-compose build

# Iniciar el contenedor
docker-compose up -d

# Verificar el estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Paso 3: Verificar Instalación

```bash
# Health check
curl http://localhost:8000/health

# Ver herramientas disponibles
curl http://localhost:8000/tools

# Documentación interactiva (Swagger)
# Abrir en navegador: http://localhost:8000/docs
```

## 📖 Uso con Claude

### Configurar en Claude Code

Agregar el servidor MCP a tu configuración de Claude Code (`.claude/settings.json` o MCP config):

```json
{
  "mcpServers": {
    "odoo": {
      "url": "http://localhost:8000",
      "transport": "http"
    }
  }
}
```

### Ejemplos de Prompts para Claude

```
"Muéstrame las ventas de los últimos 30 días"

"¿Qué clientes están en riesgo de perderse?"

"Dame un análisis completo de rendimiento del equipo de ventas"

"¿Cuáles son los 10 productos más vendidos este trimestre?"

"Busca clientes que contengan 'García' en su nombre"

"Analiza el pipeline de oportunidades con probabilidad mayor al 50%"
```

## 🔧 Comandos Útiles

### Gestión del Contenedor

```bash
# Ver logs en tiempo real
docker-compose logs -f odoo-mcp

# Reiniciar el servicio
docker-compose restart

# Detener el servicio
docker-compose down

# Reconstruir después de cambios en el código
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Ver estadísticas de recursos
docker stats odoo-mcp-server
```

### Desarrollo

```bash
# Ejecutar tests (dentro del contenedor)
docker exec -it odoo-mcp-server python -m pytest

# Acceder a shell del contenedor
docker exec -it odoo-mcp-server bash

# Ver variables de entorno
docker exec odoo-mcp-server env | grep ODOO
```

## 📊 Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servidor |
| `/health` | GET | Health check + estado conexión Odoo |
| `/tools` | GET | Lista de herramientas disponibles |
| `/get_sales_data` | POST | Datos de ventas con filtros |
| `/get_customer_insights` | POST | Segmentación RFM de clientes |
| `/get_crm_opportunities` | POST | Análisis del pipeline CRM |
| `/get_product_performance` | POST | Ranking de productos |
| `/get_sales_team_performance` | POST | Métricas del equipo |
| `/search_customers` | POST | Búsqueda de clientes |
| `/get_comprehensive_data` | POST | Análisis completo |

## 🔒 Seguridad

### Recomendaciones

1. **API Key**: Usa un usuario de integración dedicado en Odoo con permisos limitados
2. **Network**: En producción, usa una red Docker privada
3. **HTTPS**: Configura un reverse proxy (Nginx/Traefik) con SSL
4. **Firewall**: Limita el acceso al puerto 8000 solo desde localhost o IPs autorizadas

### Permisos Necesarios en Odoo

El usuario de integración debe tener acceso a:
- Ventas (`sale.order`)
- Clientes (`res.partner`)
- CRM (`crm.lead`)
- Productos (`product.product`, `sale.order.line`)

## 🐛 Troubleshooting

### Error: "Authentication failed"

```bash
# Verificar credenciales
docker logs odoo-mcp-server | grep -i auth

# Comprobar que ODOO_API_KEY es válida en Odoo UI
# Regenerar API Key si es necesario
```

### Error: "Connection refused"

```bash
# Verificar que Odoo está accesible
curl -I http://tu-instancia.odoo.com/

# Verificar red Docker
docker network inspect odoo-mcp-server_odoo-network
```

### El contenedor no arranca

```bash
# Ver logs completos
docker-compose logs odoo-mcp

# Verificar sintaxis del .env
cat .env

# Rebuild completo
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Health check falla

```bash
# Verificar salud manualmente
docker exec odoo-mcp-server curl -f http://localhost:8000/health

# Ver logs del health check
docker inspect odoo-mcp-server | jq '.[0].State.Health'
```

## 📦 Estructura del Proyecto

```
odoo-mcp-server/
├── odoo_mcp_api.py       # Código principal FastAPI + lógica MCP
├── requirements.txt      # Dependencias Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación Docker
├── .env.example          # Template de variables de entorno
├── .gitignore            # Archivos a ignorar en Git
└── README.md             # Esta documentación
```

## 🔄 Actualización

```bash
# Pull últimos cambios
git pull

# Rebuild y restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verificar versión
curl http://localhost:8000/ | jq '.version'
```

## 📝 Changelog

### v1.0.1 (Actual)
- ✅ Fix: Manejo correcto de `product_id` nulos en rendimiento de productos
- ✅ Implementación de segmentación RFM avanzada
- ✅ Health check mejorado con estado de conexión Odoo
- ✅ Logging estructurado con emojis

### v1.0.0
- 🎉 Release inicial
- 📊 7 herramientas MCP implementadas
- 🔐 Autenticación XML-RPC con API Key
- 🏥 Health checks automáticos

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-herramienta`)
3. Commit tus cambios (`git commit -am 'Añade nueva herramienta'`)
4. Push a la rama (`git push origin feature/nueva-herramienta`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🆘 Soporte

Si encuentras problemas:

1. Revisa la sección de **Troubleshooting**
2. Consulta los logs: `docker-compose logs -f`
3. Verifica el health endpoint: `curl http://localhost:8000/health`
4. Abre un issue en el repositorio del proyecto

---

**Desarrollado para integración con Claude AI** 🤖
