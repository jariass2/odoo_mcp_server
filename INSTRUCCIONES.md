# 📦 Odoo MCP Server v1.2.0

## ✅ Versión Actual: 1.2.0 - Análisis Territorial Exhaustivo

Servidor MCP con capacidades avanzadas de análisis territorial que incluye segmentación RFM, análisis temporal (MoM), métricas de concentración y detección de oportunidades de expansión.

## 📁 Archivos Incluidos

```
odoo-mcp-server/
├── odoo_mcp_api.py        ← Código principal (FastAPI + lógica MCP)
├── requirements.txt       ← Dependencias Python
├── Dockerfile             ← Configuración Docker
├── docker-compose.yml     ← Orquestación de contenedores
├── .env                   ← Credenciales actuales (PRODUCCIÓN)
├── .env.example           ← Template para nuevas instalaciones
├── .gitignore             ← Archivos a ignorar en Git
├── install.sh             ← Script de instalación automatizada
├── README.md              ← Documentación completa
└── INSTRUCCIONES.md       ← Este archivo
```

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
cd /root/odoo-mcp-server
bash install.sh
```

El script verificará Docker, construirá la imagen y iniciará el contenedor.

### Opción 2: Manual

```bash
cd /root/odoo-mcp-server

# 1. Verificar/editar credenciales
nano .env

# 2. Construir imagen
docker-compose build

# 3. Iniciar contenedor
docker-compose up -d

# 4. Verificar estado
docker-compose ps
curl http://localhost:8000/health
```

## 🔧 Para Nueva Instalación en Otro Servidor

1. **Copiar todo el directorio** a la nueva máquina:
   ```bash
   # Desde el servidor origen
   cd /root
   tar -czf odoo-mcp-server.tar.gz odoo-mcp-server/

   # Transferir a destino (ejemplo con scp)
   scp odoo-mcp-server.tar.gz usuario@servidor-destino:/ruta/destino/

   # En servidor destino
   tar -xzf odoo-mcp-server.tar.gz
   cd odoo-mcp-server
   ```

2. **Configurar credenciales**:
   ```bash
   # Copiar template
   cp .env.example .env

   # Editar con tus credenciales
   nano .env
   ```

3. **Instalar**:
   ```bash
   bash install.sh
   ```

## 🔐 Configuración de Credenciales

El archivo `.env` actual contiene las credenciales del servidor de producción:

```
ODOO_URL=http://sandrodesii.odoo.com/
ODOO_DB=sandrodesii-v14-produccion-3259284
ODOO_USERNAME=integracion@sandrodesii.com
ODOO_API_KEY=0f2db9888eb093bc40123806e8065cdad2fde41d
```

### Para Generar Nueva API Key en Odoo:

1. Inicia sesión en Odoo
2. Ve a **Preferencias** (clic en tu nombre arriba a la derecha)
3. Selecciona **Seguridad**
4. En la sección **API Keys**, haz clic en **Nueva API Key**
5. Dale un nombre (ej: "MCP Server Claude")
6. Copia la clave generada y pégala en `ODOO_API_KEY`

## 🧪 Verificación Post-Instalación

```bash
# 1. Health check
curl http://localhost:8000/health

# Respuesta esperada:
# {
#   "status": "healthy",
#   "odoo_connected": true,
#   "odoo_uid": 123,
#   ...
# }

# 2. Ver herramientas disponibles
curl http://localhost:8000/tools

# 3. Documentación interactiva (Swagger)
# Abrir en navegador: http://localhost:8000/docs

# 4. Ver logs en tiempo real
docker-compose logs -f odoo-mcp
```

## 📊 Integración con Claude Code

### Configurar MCP Server en Claude

1. Edita tu configuración de Claude Code:
   ```bash
   nano ~/.claude/settings.json
   ```

2. Agrega el servidor MCP:
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

3. Reinicia Claude Code

### Probar con Claude

#### Prompts Básicos:
```
"Muéstrame las ventas de los últimos 30 días"

"Dame un análisis de clientes en riesgo"

"¿Cuáles son los productos más vendidos?"

"Analiza el rendimiento del equipo de ventas"
```

#### Prompts de Análisis Territorial (v1.2.0):
```
"Dame un análisis territorial exhaustivo de los últimos 30 días"

"¿Qué provincias están creciendo más rápido?"

"Muéstrame qué ciudades tienen potencial de expansión"

"¿Cuáles provincias tienen más clientes VIP?"

"Identifica territorios con alta concentración de ventas"

"¿Dónde están los clientes en riesgo por provincia?"

"Compara el crecimiento territorial del mes actual vs anterior"

"¿Qué productos se venden más en cada provincia?"

"Muéstrame oportunidades de expansión territorial"
```

## 🔄 Comandos Útiles

```bash
# Ver estado del contenedor
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Reconstruir después de cambios
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Acceder al contenedor
docker exec -it odoo-mcp-server bash

# Ver uso de recursos
docker stats odoo-mcp-server
```

## 🐛 Troubleshooting

### El contenedor no arranca

```bash
# Ver logs detallados
docker-compose logs

# Verificar que el puerto 8000 no esté ocupado
netstat -tuln | grep 8000

# Rebuild completo
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Error de autenticación con Odoo

```bash
# Verificar credenciales
cat .env

# Ver logs del servidor
docker-compose logs odoo-mcp | grep -i auth

# Verificar conectividad con Odoo
curl -I http://sandrodesii.odoo.com/
```

### Health check falla

```bash
# Verificar manualmente
curl http://localhost:8000/health

# Ver estado del health check
docker inspect odoo-mcp-server | grep -A 10 Health
```

## 📦 Control de Versiones (Git)

Si quieres versionar el proyecto:

```bash
cd /root/odoo-mcp-server

# Inicializar repositorio
git init

# Agregar archivos (el .env ya está en .gitignore)
git add .

# Primer commit
git commit -m "Initial commit: Odoo MCP Server"

# Conectar con repositorio remoto (opcional)
git remote add origin https://github.com/tu-usuario/odoo-mcp-server.git
git push -u origin main
```

**IMPORTANTE:** El archivo `.env` está en `.gitignore` para no subir credenciales a Git.

## 📚 Documentación Adicional

- **README.md**: Documentación completa del proyecto
- **Swagger UI**: http://localhost:8000/docs (cuando el servidor esté corriendo)
- **ReDoc**: http://localhost:8000/redoc (documentación alternativa)

## ✅ Checklist de Instalación

- [ ] Docker y Docker Compose instalados
- [ ] Archivos descargados/copiados
- [ ] Archivo `.env` configurado con credenciales válidas
- [ ] Imagen Docker construida (`docker-compose build`)
- [ ] Contenedor iniciado (`docker-compose up -d`)
- [ ] Health check exitoso (`curl http://localhost:8000/health`)
- [ ] MCP Server configurado en Claude Code
- [ ] Pruebas con Claude exitosas

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica el health endpoint: `curl http://localhost:8000/health`
3. Consulta la sección de Troubleshooting en README.md
4. Verifica las credenciales de Odoo en el archivo `.env`

---

**¡Proyecto listo para usar! 🚀**
