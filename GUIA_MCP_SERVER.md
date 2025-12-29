# Guía Completa del Odoo MCP Server

## Índice
1. [Introducción](#introducción)
2. [Lista de Herramientas Disponibles](#lista-de-herramientas-disponibles)
3. [Herramientas Detalladas](#herramientas-detalladas)
   - [Sales Data](#1-sales-data)
   - [Customer Insights](#2-customer-insights)
   - [CRM Opportunities](#3-crm-opportunities)
   - [Product Performance](#4-product-performance)
   - [Sales Team Performance](#5-sales-team-performance)
   - [Customer Search](#6-customer-search)
   - [Territorial Analysis](#7-territorial-analysis)
   - [Category Analysis](#8-category-analysis)
   - [Comprehensive Data](#9-comprehensive-data)
4. [Casos de Uso por Rol](#casos-de-uso-por-rol)
5. [Flujos de Análisis Recomendados](#flujos-de-análisis-recomendados)

---

## Introducción

El **Odoo MCP Server** es un servidor que implementa el protocolo MCP (Model Context Protocol) para exponer datos de Odoo a Claude AI. Actúa como un puente inteligente entre tu instancia de Odoo y Claude, permitiendo análisis avanzados de datos empresariales mediante lenguaje natural.

**Versión actual:** v1.3.0
**Tecnología:** FastAPI + XML-RPC
**Puerto:** 8000

---

## Lista de Herramientas Disponibles

| # | Herramienta | Descripción Corta | Endpoint |
|---|-------------|-------------------|----------|
| 1 | **Sales Data** | Datos de ventas con filtros avanzados | `/get_sales_data` |
| 2 | **Customer Insights** | Segmentación RFM de clientes | `/get_customer_insights` |
| 3 | **CRM Opportunities** | Pipeline de oportunidades comerciales | `/get_crm_opportunities` |
| 4 | **Product Performance** | Ranking de productos por rendimiento | `/get_product_performance` |
| 5 | **Sales Team Performance** | Métricas del equipo comercial | `/get_sales_team_performance` |
| 6 | **Customer Search** | Búsqueda rápida de clientes | `/search_customers` |
| 7 | **Territorial Analysis** | Análisis territorial exhaustivo | `/get_territorial_analysis` |
| 8 | **Category Analysis** | Análisis por tipo de negocio (Hotel, Restaurante, etc.) | `/get_category_analysis` |
| 9 | **Comprehensive Data** | Análisis completo en una sola llamada | `/get_comprehensive_data` |

---

## Herramientas Detalladas

### 1. Sales Data

**Endpoint:** `POST /get_sales_data`

#### Descripción
Obtiene datos detallados de órdenes de venta desde Odoo con capacidad de filtrado avanzado. Recupera información transaccional completa y calcula métricas agregadas automáticamente.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `days_back` | int | No | 30 | Número de días hacia atrás para filtrar |
| `state` | string | No | None | Estado de la orden (sale, done, draft, etc.) |
| `partner_ids` | array[int] | No | None | IDs de clientes específicos a filtrar |
| `min_amount` | float | No | None | Monto mínimo de la orden |

#### Información que Captura

**Datos de cada orden:**
- ID y nombre de la orden
- Cliente (partner_id y nombre)
- Fecha de orden
- Monto total (amount_total)
- Estado de la orden
- Usuario responsable (vendedor)
- Equipo de ventas (team_id)

**Métricas calculadas:**
- Total de ingresos del período
- Valor promedio de orden
- Número de órdenes
- Rango de fechas analizado

#### Preguntas Tipo que Responde

- "¿Cuáles fueron las ventas de los últimos 30 días?"
- "Muéstrame todas las órdenes confirmadas del último mes"
- "¿Qué ventas superaron los 5,000 euros en el último trimestre?"
- "Dame las ventas del cliente ID 123 en los últimos 60 días"
- "¿Cuál es el ticket promedio de este mes?"
- "¿Cuántos pedidos hemos cerrado esta semana?"

#### Casos de Uso

1. **Análisis de tendencias:** Identificar patrones de venta por período
2. **Seguimiento de metas:** Comparar ingresos actuales vs objetivos
3. **Análisis de clientes específicos:** Estudiar comportamiento de compra
4. **Detección de anomalías:** Identificar órdenes inusuales o problemas
5. **Reporte ejecutivo:** Datos para dashboard de ventas

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 145,
  "data": [
    {
      "name": "SO00012345",
      "partner_id": [456, "Cliente Ejemplo S.L."],
      "date_order": "2025-12-15 10:30:00",
      "amount_total": 2450.50,
      "state": "sale",
      "user_id": [78, "Juan Pérez"],
      "team_id": [5, "Equipo Nacional"]
    }
  ],
  "summary": {
    "total_revenue": 325480.75,
    "avg_order_value": 2244.69,
    "period_days": 30,
    "date_from": "2025-11-29",
    "date_to": "2025-12-29"
  }
}
```

---

### 2. Customer Insights

**Endpoint:** `POST /get_customer_insights`

#### Descripción
Analiza el comportamiento de clientes mediante segmentación RFM (Recency, Frequency, Monetary). Incluye datos geográficos completos para cada cliente. Es la herramienta más potente para entender la base de clientes.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `segment` | string | No | "all" | Segmento a filtrar: all, vip, at_risk, new, inactive, regular |
| `min_purchases` | int | No | None | Número mínimo de compras |
| `min_revenue` | float | No | None | Ingresos mínimos generados |

#### Segmentación RFM Automática

La herramienta clasifica automáticamente a cada cliente en:

- **VIP:** Facturación > €10,000 + más de 5 compras
- **At Risk:** Clientes recurrentes (>2 compras) sin actividad en 180+ días
- **New:** Primera compra en los últimos 30 días
- **Inactive:** Sin compras en más de 365 días
- **Regular:** Resto de clientes activos

#### Información que Captura

**Datos de identificación:**
- ID del partner
- Nombre, email, teléfono, móvil
- Referencia interna (ref)

**Datos geográficos:**
- Calle (street, street2)
- Ciudad (city)
- Provincia/Estado (state_id)
- Código postal (zip)
- País (country_id)
- NIF/CIF (vat)

**Métricas de comportamiento:**
- Ingresos totales generados
- Número de compras
- Valor promedio de pedido
- Fecha de última compra
- Días desde última compra
- Segmento RFM asignado
- Cliente desde (fecha de creación)
- LTV Score (valor de vida ajustado por recencia)

**Métricas agregadas:**
- Distribución por segmento
- Ingresos totales de la base
- Promedio de ingresos por cliente

#### Preguntas Tipo que Responde

**Segmentación:**
- "¿Quiénes son mis clientes VIP?"
- "¿Qué clientes están en riesgo de perderse?"
- "Muéstrame los clientes nuevos del último mes"
- "¿Cuántos clientes inactivos tengo?"

**Análisis geográfico:**
- "¿Dónde están ubicados mis clientes VIP?"
- "¿Qué clientes tengo en Barcelona?"
- "Muéstrame la distribución de clientes por provincia"

**Análisis de valor:**
- "¿Cuáles son los 10 clientes que más facturan?"
- "¿Qué clientes tienen un ticket promedio superior a 1,000€?"
- "Clientes con más de 10 compras realizadas"

**Estrategia comercial:**
- "¿Qué clientes no compran desde hace más de 6 meses?"
- "¿Cuántos clientes en riesgo tengo en Madrid?"
- "¿Cuál es el valor de vida promedio de mis clientes?"

#### Casos de Uso

1. **Retención:** Identificar y contactar clientes en riesgo
2. **Upselling:** Encontrar clientes regulares con potencial VIP
3. **Expansión territorial:** Analizar cobertura geográfica
4. **Campañas segmentadas:** Crear listas de contactos por segmento
5. **Pronóstico de ingresos:** Estimar valor futuro por segmento

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 234,
  "data": [
    {
      "partner_id": 789,
      "name": "Empresa XYZ S.A.",
      "email": "contacto@xyz.com",
      "phone": "+34 912 345 678",
      "mobile": "+34 600 123 456",
      "street": "Calle Mayor, 123",
      "city": "Madrid",
      "state_id": [15, "Madrid"],
      "zip": "28013",
      "country_id": [68, "España"],
      "vat": "ESB12345678",
      "total_revenue": 45680.50,
      "num_purchases": 12,
      "avg_order_value": 3806.71,
      "last_order_date": "2025-11-20",
      "days_since_last": 39,
      "segment": "vip",
      "customer_since": "2023-03-15",
      "ltv_score": 40123.45
    }
  ],
  "summary": {
    "segments": {
      "vip": 23,
      "regular": 156,
      "at_risk": 34,
      "new": 15,
      "inactive": 6
    },
    "total_revenue": 2456780.90,
    "avg_revenue_per_customer": 10498.21
  }
}
```

---

### 3. CRM Opportunities

**Endpoint:** `POST /get_crm_opportunities`

#### Descripción
Obtiene y analiza el pipeline de oportunidades comerciales desde el módulo CRM de Odoo. Calcula automáticamente métricas ponderadas por probabilidad.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `stage` | string | No | None | Nombre de la etapa del pipeline |
| `min_probability` | int | No | None | Probabilidad mínima de cierre (0-100) |
| `days_inactive` | int | No | None | Días de inactividad (sin actualizaciones) |

#### Información que Captura

**Datos de la oportunidad:**
- Nombre de la oportunidad
- Cliente asociado (partner_id)
- Ingresos esperados (expected_revenue)
- Probabilidad de cierre (0-100%)
- Etapa del pipeline (stage_id)
- Usuario responsable
- Equipo de ventas
- Fecha límite (deadline)
- Fecha de creación
- Última actualización

**Métricas del pipeline:**
- Número total de oportunidades
- Valor total del pipeline
- Valor ponderado por probabilidad
- Tamaño promedio de deal
- Probabilidad promedio

#### Preguntas Tipo que Responde

**Pipeline general:**
- "¿Cuál es el valor total de mi pipeline?"
- "¿Cuántas oportunidades tengo abiertas?"
- "¿Cuál es el deal promedio que manejamos?"

**Filtrado por probabilidad:**
- "Muéstrame oportunidades con más del 70% de probabilidad"
- "¿Qué deals son casi seguros de cerrar?"
- "¿Cuál es el valor ponderado del pipeline?"

**Gestión de pipeline:**
- "¿Qué oportunidades están estancadas por más de 30 días?"
- "¿Qué deals están en etapa de negociación?"
- "Oportunidades que vencen este mes"

**Por equipo/vendedor:**
- "¿Cuál es el pipeline del equipo de Juan?"
- "¿Qué vendedor tiene más oportunidades?"

#### Casos de Uso

1. **Pronóstico de ventas:** Calcular ingresos esperados
2. **Priorización:** Identificar deals de alto valor y alta probabilidad
3. **Gestión de tiempo:** Detectar oportunidades estancadas
4. **Performance comercial:** Evaluar pipeline por vendedor
5. **Planificación de recursos:** Asignar esfuerzos según valor esperado

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 67,
  "data": [
    {
      "name": "Proyecto Implementación ERP",
      "partner_id": [456, "Cliente ABC"],
      "expected_revenue": 125000.00,
      "probability": 75,
      "stage_id": [3, "Propuesta Enviada"],
      "user_id": [12, "María García"],
      "team_id": [2, "Grandes Cuentas"],
      "date_deadline": "2026-01-15",
      "create_date": "2025-11-01",
      "write_date": "2025-12-20"
    }
  ],
  "pipeline_metrics": {
    "total_opportunities": 67,
    "total_pipeline_value": 3450000.00,
    "weighted_pipeline_value": 1725000.00,
    "avg_deal_size": 51492.54,
    "avg_probability": 50.15
  }
}
```

---

### 4. Product Performance

**Endpoint:** `POST /get_product_performance`

#### Descripción
Analiza el rendimiento de productos basándose en ventas reales. Genera un ranking de productos por ingresos y cantidad vendida.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `days_back` | int | No | 90 | Días hacia atrás para analizar |
| `top_n` | int | No | 20 | Número de productos a retornar en el ranking |

#### Información que Captura

**Por producto:**
- ID del producto
- Nombre del producto
- Cantidad total vendida
- Ingresos totales generados

**Métricas agregadas:**
- Total de productos únicos vendidos
- Ingresos totales de productos
- Período analizado
- Número de líneas de pedido omitidas (sin producto)

#### Preguntas Tipo que Responde

**Rendimiento:**
- "¿Cuáles son los 10 productos más vendidos?"
- "¿Qué producto genera más ingresos?"
- "Productos con más de 100 unidades vendidas"

**Análisis estratégico:**
- "¿Qué productos deberíamos promocionar más?"
- "¿Qué representa mi top 5 de productos del total de ventas?"
- "¿Cuál es el producto estrella del trimestre?"

**Inventario y compras:**
- "¿Qué productos tienen más rotación?"
- "¿Qué productos comprar para el próximo mes?"

#### Casos de Uso

1. **Gestión de inventario:** Priorizar stock de productos top
2. **Marketing:** Identificar productos para campañas
3. **Análisis ABC:** Clasificar productos por importancia
4. **Negociación con proveedores:** Datos para mejores precios en productos clave
5. **Descatalogación:** Identificar productos de bajo rendimiento

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 156,
  "data": [
    {
      "product_id": 234,
      "product_name": "Laptop Dell XPS 15",
      "total_qty_sold": 45.0,
      "total_revenue": 67500.00
    },
    {
      "product_id": 567,
      "product_name": "Monitor LG 27 pulgadas",
      "total_qty_sold": 123.0,
      "total_revenue": 36900.00
    }
  ],
  "summary": {
    "total_products": 156,
    "total_revenue": 456789.50,
    "period_days": 90,
    "skipped_lines": 3
  }
}
```

---

### 5. Sales Team Performance

**Endpoint:** `POST /get_sales_team_performance`

#### Descripción
Analiza el rendimiento individual de cada miembro del equipo de ventas basándose en órdenes confirmadas.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `days_back` | int | No | 30 | Número de días hacia atrás para analizar |

#### Información que Captura

**Por vendedor:**
- ID del usuario
- Nombre del vendedor
- Ingresos totales generados
- Número de deals cerrados
- Tamaño promedio de deal

**Métricas del equipo:**
- Ingresos totales del equipo
- Total de deals cerrados
- Tamaño promedio de deal global
- Período analizado

#### Preguntas Tipo que Responde

**Performance individual:**
- "¿Quién es el mejor vendedor del mes?"
- "¿Cuánto ha facturado Juan este trimestre?"
- "¿Qué vendedor tiene el mejor ticket promedio?"

**Gestión de equipo:**
- "¿Cómo se distribuyen las ventas entre el equipo?"
- "¿Quién necesita apoyo o coaching?"
- "¿Qué vendedor cierra más deals?"

**Compensación:**
- "Cálculo de comisiones por vendedor"
- "¿Quién supera su meta este mes?"

**Planificación:**
- "¿Necesitamos contratar más vendedores?"
- "¿Qué capacidad de venta tiene el equipo?"

#### Casos de Uso

1. **Evaluación de desempeño:** Datos objetivos para reviews
2. **Incentivos y comisiones:** Base para cálculo de bonos
3. **Detección de problemas:** Identificar bajo rendimiento
4. **Reconocimiento:** Celebrar logros del equipo
5. **Redistribución de cartera:** Balancear carga de trabajo

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 8,
  "data": [
    {
      "user_id": 12,
      "user_name": "Carlos Rodríguez",
      "total_revenue": 145680.50,
      "num_deals": 23,
      "avg_deal_size": 6334.37
    },
    {
      "user_id": 15,
      "user_name": "Ana Martínez",
      "total_revenue": 132450.00,
      "num_deals": 31,
      "avg_deal_size": 4272.58
    }
  ],
  "team_summary": {
    "total_revenue": 678920.75,
    "total_deals": 145,
    "avg_deal_size": 4682.21,
    "period_days": 30
  }
}
```

---

### 6. Customer Search

**Endpoint:** `POST /search_customers`

#### Descripción
Búsqueda rápida y flexible de clientes por múltiples criterios. Incluye datos geográficos completos para cada resultado.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `query` | string | Sí | - | Texto a buscar (nombre, email, teléfono, ref) |
| `limit` | int | No | 10 | Número máximo de resultados |

#### Información que Captura

**Datos de identificación:**
- Nombre del cliente
- Email, teléfono, móvil
- Referencia interna (ref)
- Comentarios/notas

**Datos geográficos:**
- Dirección completa (street, street2)
- Ciudad, provincia, código postal
- País
- NIF/CIF (vat)

**Métricas de actividad:**
- Ranking como cliente (customer_rank)
- Ranking como proveedor (supplier_rank)
- Número de órdenes de venta (sale_order_count)
- Fechas de creación y última modificación

#### Preguntas Tipo que Responde

**Búsqueda básica:**
- "Busca el cliente García"
- "Encuentra clientes con email @gmail.com"
- "Buscar por teléfono 912345678"

**Búsqueda por referencia:**
- "Cliente con referencia CLI-2024-001"
- "Buscar por CIF B12345678"

**Verificación:**
- "¿Existe el cliente XYZ en el sistema?"
- "¿Cuál es la dirección de Cliente ABC?"

#### Casos de Uso

1. **Atención al cliente:** Localizar rápidamente información de cliente
2. **Ventas:** Verificar si un prospecto ya existe
3. **Limpieza de datos:** Encontrar duplicados
4. **Validación:** Confirmar datos de contacto
5. **Seguimiento:** Acceder rápido a historial de cliente

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 456,
      "name": "García e Hijos S.L.",
      "email": "info@garcia.com",
      "phone": "+34 912 345 678",
      "mobile": "+34 600 111 222",
      "street": "Calle Comercio, 45",
      "city": "Valencia",
      "state_id": [20, "Valencia"],
      "zip": "46001",
      "country_id": [68, "España"],
      "vat": "ESB98765432",
      "customer_rank": 1,
      "supplier_rank": 0,
      "sale_order_count": 15,
      "create_date": "2024-02-10",
      "write_date": "2025-12-15",
      "ref": "CLI-2024-089"
    }
  ],
  "query": "garcia"
}
```

---

### 7. Territorial Analysis

**Endpoint:** `POST /get_territorial_analysis`

#### Descripción
Herramienta más avanzada del servidor (v1.2.0). Proporciona análisis territorial exhaustivo con múltiples dimensiones: ventas, clientes, productos, vendedores, segmentación RFM, análisis temporal, concentración de mercado y oportunidades de expansión.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `days_back` | int | No | 30 | Número de días hacia atrás para analizar |

#### Información que Captura

**Por provincia (state):**

1. **Métricas básicas:**
   - Ingresos totales
   - Número de pedidos
   - Número de clientes únicos
   - Valor promedio de pedido

2. **Top 5 ciudades:**
   - Ingresos por ciudad
   - Número de pedidos
   - Número de clientes

3. **Top 5 productos:**
   - Productos más vendidos en la provincia
   - Cantidad vendida
   - Ingresos generados

4. **Vendedores activos:**
   - Vendedores operando en la zona
   - Ingresos por vendedor
   - Número de deals por vendedor

5. **Segmentación RFM territorial (NUEVO v1.2.0):**
   - Clientes VIP por provincia
   - Clientes en riesgo
   - Clientes nuevos
   - Clientes inactivos
   - Clientes regulares

6. **Análisis temporal (NUEVO v1.2.0):**
   - Ingresos del período actual
   - Ingresos del período anterior
   - Tasa de crecimiento (%)
   - Crecimiento en valor absoluto

7. **Métricas de concentración (NUEVO v1.2.0):**
   - Total de ciudades en la provincia
   - Concentración en top 3 ciudades (%)

8. **Oportunidades de expansión (NUEVO v1.2.0):**
   - Ciudades con 1-2 clientes (alto potencial)
   - Lista de ciudades potenciales

**Métricas globales agregadas:**

- Total de ingresos
- Total de provincias
- Total de pedidos
- Total de clientes
- Total de ciudades

- **Segmentación RFM global:**
  - Total VIP, At Risk, New, Inactive, Regular

- **Crecimiento global:**
  - Ingresos período actual vs anterior
  - Tasa de crecimiento global
  - Top 5 provincias de mayor crecimiento

- **Insights de expansión:**
  - Total de oportunidades de expansión
  - Provincias con alta concentración (>80%)
  - Territorios subatendidos (<5 clientes)

#### Preguntas Tipo que Responde

**Análisis geográfico básico:**
- "¿Qué provincia genera más ingresos?"
- "¿En cuántas provincias operamos?"
- "¿Cuáles son las top 5 ciudades por ventas?"

**Segmentación territorial:**
- "¿Dónde están concentrados mis clientes VIP?"
- "¿Qué provincias tienen más clientes en riesgo?"
- "¿En qué zonas tenemos clientes nuevos?"

**Análisis de crecimiento:**
- "¿Qué provincias están creciendo más rápido?"
- "¿Dónde hemos perdido facturación respecto al mes pasado?"
- "¿Cuál es la tasa de crecimiento territorial global?"

**Oportunidades de negocio:**
- "¿En qué ciudades podemos expandirnos?"
- "¿Qué territorios están subatendidos?"
- "¿Dónde hay ciudades con pocos clientes pero potencial?"

**Productos por zona:**
- "¿Qué productos se venden más en Andalucía?"
- "¿Hay diferencias en preferencias de producto por región?"

**Cobertura comercial:**
- "¿Qué vendedores operan en cada provincia?"
- "¿Necesitamos más vendedores en alguna zona?"

**Concentración de mercado:**
- "¿Dónde está muy concentrado el negocio?"
- "¿Qué provincias tienen una distribución más equilibrada?"

#### Casos de Uso

1. **Expansión comercial:** Identificar zonas de crecimiento
2. **Asignación de territorios:** Distribuir vendedores eficientemente
3. **Estrategia de producto:** Adaptar oferta por región
4. **Retención regional:** Detectar problemas territoriales
5. **Inversión en marketing:** Priorizar zonas por ROI
6. **Apertura de oficinas:** Decidir ubicaciones estratégicas
7. **Gestión de riesgo:** Diversificar concentración territorial
8. **Análisis competitivo:** Identificar fortalezas y debilidades por zona

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 15,
  "data": [
    {
      "state": "Madrid",
      "total_revenue": 345680.50,
      "num_orders": 234,
      "num_customers": 89,
      "avg_order_value": 1477.18,
      "top_cities": [
        {
          "city": "Madrid",
          "revenue": 298450.00,
          "orders": 198,
          "num_customers": 67
        },
        {
          "city": "Alcalá de Henares",
          "revenue": 23450.00,
          "orders": 18,
          "num_customers": 8
        }
      ],
      "top_products": [
        {
          "product": "Laptop Dell XPS 15",
          "qty": 23.0,
          "revenue": 34500.00
        }
      ],
      "salespeople": [
        {
          "salesperson": "Carlos Rodríguez",
          "revenue": 145680.50,
          "orders": 89
        }
      ],
      "rfm_segmentation": {
        "vip": 12,
        "at_risk": 8,
        "new": 5,
        "inactive": 3,
        "regular": 61
      },
      "growth_vs_previous_period": {
        "current_revenue": 345680.50,
        "previous_revenue": 312450.00,
        "growth_rate": 10.64,
        "growth_amount": 33230.50
      },
      "concentration_metrics": {
        "total_cities": 12,
        "top3_concentration_pct": 92.5
      },
      "expansion_opportunities": {
        "cities_with_1_2_customers": 5,
        "potential_cities": [
          {
            "city": "Pozuelo de Alarcón",
            "revenue": 4500.00,
            "orders": 2,
            "num_customers": 1
          }
        ]
      }
    }
  ],
  "summary": {
    "total_revenue": 1245680.75,
    "total_states": 15,
    "total_orders": 892,
    "total_customers": 456,
    "total_cities": 127,
    "period_days": 30,
    "top_state": "Madrid",
    "top_state_revenue": 345680.50,
    "global_rfm_segmentation": {
      "vip": 67,
      "at_risk": 45,
      "new": 28,
      "inactive": 23,
      "regular": 293
    },
    "global_growth": {
      "current_period_revenue": 1245680.75,
      "previous_period_revenue": 1123450.50,
      "growth_rate_pct": 10.88,
      "growth_amount": 122230.25
    },
    "top_growing_states": [
      {
        "state": "Valencia",
        "growth_rate": 25.4,
        "revenue": 156780.00
      },
      {
        "state": "Barcelona",
        "growth_rate": 18.2,
        "revenue": 234560.00
      }
    ],
    "expansion_insights": {
      "total_expansion_opportunities": 34,
      "states_with_high_concentration": 8,
      "underserved_territories": 3
    }
  }
}
```

---

### 8. Category Analysis

**Endpoint:** `POST /get_category_analysis`

#### Descripción
Análisis exhaustivo por categoría de cliente (tipo de negocio). Permite segmentar y analizar el rendimiento comercial por sectores específicos como CADENA HOTEL, CADENA RESTAURANTE, HELADERIA, CATERING, etc. Proporciona una vista completa del comportamiento de cada vertical de negocio.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `category_id` | int | No | None | ID de categoría específica (None = todas las categorías) |
| `days_back` | int | No | 90 | Días hacia atrás para análisis de ventas |
| `top_customers` | int | No | 10 | Número de top clientes a retornar por categoría |

#### Información que Captura

**Por cada categoría:**

1. **Identificación:**
   - ID de categoría
   - Nombre de categoría
   - Color de categoría

2. **Métricas básicas:**
   - Número total de clientes en la categoría
   - Número de clientes activos (con compras)
   - Ingresos del período analizado
   - Número de pedidos del período
   - Valor promedio de pedido

3. **Segmentación RFM por categoría:**
   - Clientes VIP en la categoría
   - Clientes en riesgo
   - Clientes nuevos
   - Clientes inactivos
   - Clientes regulares

4. **Top clientes de la categoría:**
   - Partner ID y nombre
   - Ingresos totales históricos
   - Número de compras
   - Días desde última compra
   - Segmento RFM
   - Ubicación (ciudad y provincia)

5. **Distribución geográfica:**
   - Top 10 provincias con más clientes de la categoría
   - Número de clientes por provincia

6. **Top 10 productos más vendidos:**
   - Productos más populares en cada categoría
   - Cantidad vendida
   - Ingresos generados

7. **Métricas adicionales:**
   - Ingresos totales históricos de la categoría
   - Promedio de ingresos por cliente
   - Promedio de compras por cliente

**Métricas globales agregadas:**
- Total de categorías analizadas
- Total de clientes
- Ingresos totales del período
- Total de pedidos
- Categoría líder por ingresos
- Segmentación RFM global

#### Preguntas Tipo que Responde

**Análisis por sector:**
- "¿Cómo están rindiendo mis clientes de CADENA HOTEL?"
- "¿Qué categoría de negocio genera más ingresos?"
- "¿Cuántos clientes tengo en cada categoría?"

**Segmentación por categoría:**
- "¿Cuántos clientes VIP tengo en RESTAURANTE vs HELADERIA?"
- "¿Qué categorías tienen más clientes en riesgo?"
- "¿Dónde están los clientes nuevos por sector?"

**Análisis de clientes:**
- "¿Quiénes son los mejores clientes de CATERING?"
- "¿Qué hoteles independientes facturan más?"
- "¿Cuántas heladerías están inactivas?"

**Análisis geográfico:**
- "¿Dónde se concentran los restaurantes?"
- "¿En qué provincias tengo más cadenas hoteleras?"
- "Distribución geográfica por tipo de negocio"

**Análisis de productos:**
- "¿Qué productos compran más las cadenas hoteleras?"
- "¿Hay diferencias de producto entre restaurantes y caterings?"
- "¿Qué productos prefieren las heladerías?"

**Estrategia comercial:**
- "¿Qué categoría tiene mejor ticket promedio?"
- "¿En qué sector debería enfocar mis esfuerzos comerciales?"
- "¿Qué categorías tienen más potencial de crecimiento?"

**Comparativas:**
- "Comparar rendimiento entre HOTEL INDEPENDIENTE y CADENA HOTEL"
- "¿Qué categoría es más leal (menos días desde última compra)?"
- "Diferencias de comportamiento entre sectores"

#### Casos de Uso

1. **Estrategia comercial por sector:** Identificar categorías de alto valor para enfocar recursos
2. **Desarrollo de productos:** Adaptar catálogo según necesidades de cada sector
3. **Retención por vertical:** Campañas específicas para clientes en riesgo de cada categoría
4. **Expansión sectorial:** Identificar categorías con potencial de crecimiento
5. **Pricing estratégico:** Ajustar precios según comportamiento de cada vertical
6. **Marketing segmentado:** Comunicación personalizada por tipo de negocio
7. **Análisis competitivo:** Comparar performance entre segmentos similares
8. **Asignación de vendedores:** Especializar equipos por tipo de cliente

#### Categorías Disponibles en el Sistema

- **CADENA HOTEL** - Cadenas hoteleras
- **CADENA RESTAURANTE** - Cadenas de restaurantes
- **CAMPING** - Campings y alojamientos al aire libre
- **CATERING** - Empresas de catering y eventos
- **COCTELERIA** - Bares y coctelería
- **COLECTIVIDAD** - Colectividades y comedores
- **DISTRIBUCIÓN** - Distribuidores mayoristas
- **ECOMMERCE** - Comercio electrónico
- **EXPORT** - Exportación
- **GRAN CUENTA** - Grandes cuentas corporativas
- **GRUPAJE** - Grupaje y logística
- **HELADERIA** - Heladerías
- **HOTEL INDEPENDIENTE** - Hoteles independientes
- **INDEPENDIENTE** - Negocios independientes
- **PASTISSERIE/CAFETERIA** - Pastelerías y cafeterías
- **RESTAURANTE** - Restaurantes independientes
- **SUPERMERCADO** - Supermercados
- **TIENDA INDEPENDIENTE** - Tiendas independientes
- **TIENDA/RESTAURANTE** - Negocios mixtos

#### Ejemplo de Respuesta

```json
{
  "success": true,
  "count": 18,
  "data": [
    {
      "category_id": 8,
      "category_name": "CADENA RESTAURANTE",
      "category_color": 2,
      "num_customers": 45,
      "num_active_customers": 38,
      "revenue_period": 235680.50,
      "num_orders_period": 156,
      "avg_order_value": 1510.77,
      "rfm_segmentation": {
        "vip": 12,
        "at_risk": 5,
        "new": 2,
        "inactive": 1,
        "regular": 18
      },
      "top_customers": [
        {
          "partner_id": 12345,
          "name": "Cadena Restaurante ABC",
          "total_revenue": 145680.00,
          "num_purchases": 45,
          "days_since_last": 3,
          "segment": "vip",
          "city": "Barcelona",
          "state": "Barcelona (ES)"
        },
        {
          "partner_id": 12346,
          "name": "Grupo Gastronómico XYZ",
          "total_revenue": 98450.50,
          "num_purchases": 32,
          "days_since_last": 7,
          "segment": "vip",
          "city": "Madrid",
          "state": "Madrid (ES)"
        }
      ],
      "geographic_distribution": [
        {
          "state": "Barcelona (ES)",
          "num_customers": 15
        },
        {
          "state": "Madrid (ES)",
          "num_customers": 12
        },
        {
          "state": "València (Valencia) (ES)",
          "num_customers": 8
        }
      ],
      "top_products": [
        {
          "product_name": "Helado Premium 5L",
          "qty": 450.0,
          "revenue": 45000.00
        },
        {
          "product_name": "Sorbete Limón 5L",
          "qty": 320.0,
          "revenue": 28800.00
        }
      ],
      "metrics": {
        "total_lifetime_revenue": 1245680.75,
        "avg_revenue_per_customer": 32781.07,
        "avg_purchases_per_customer": 28.5
      }
    }
  ],
  "summary": {
    "total_categories": 18,
    "total_customers": 456,
    "total_revenue_period": 1456780.90,
    "total_orders_period": 1234,
    "avg_order_value": 1180.50,
    "period_days": 90,
    "date_from": "2025-10-01",
    "date_to": "2025-12-29",
    "top_category": "CADENA RESTAURANTE",
    "top_category_revenue": 235680.50,
    "global_rfm_segmentation": {
      "vip": 89,
      "at_risk": 45,
      "new": 23,
      "inactive": 12,
      "regular": 287
    }
  }
}
```

---

### 9. Comprehensive Data

**Endpoint:** `POST /get_comprehensive_data`

#### Descripción
Endpoint especial que ejecuta TODAS las herramientas en una sola llamada. Ideal para análisis completos y dashboards ejecutivos. Optimiza múltiples llamadas en una sola operación.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `days_back` | int | No | 30 | Número de días para análisis temporal |

#### Información que Captura

Ejecuta internamente:
1. `get_sales_data`
2. `get_customer_insights`
3. `get_crm_opportunities`
4. `get_product_performance`
5. `get_sales_team_performance`
6. `get_territorial_analysis`
7. `get_category_analysis`

Y devuelve:
- Todos los datos de cada herramienta
- Un resumen ejecutivo consolidado con KPIs clave (incluye categoría líder)

#### Preguntas Tipo que Responde

**Análisis ejecutivo:**
- "Dame un análisis completo del negocio"
- "¿Cómo está la empresa en general?"
- "Necesito un dashboard ejecutivo del último mes"

**Reportes periódicos:**
- "Genera el reporte mensual completo"
- "¿Cuáles son todos los KPIs importantes?"

**Decisiones estratégicas:**
- "¿Dónde deberíamos enfocar recursos?"
- "¿Cuál es el estado global del negocio?"

#### Casos de Uso

1. **Reportes ejecutivos:** Un solo endpoint para directivos
2. **Dashboards:** Alimentar cuadros de mando completos
3. **Análisis holístico:** Ver todas las dimensiones del negocio
4. **Onboarding de Claude:** Dar contexto completo en una llamada
5. **Auditorías:** Snapshot completo del estado del negocio

#### Ejemplo de Respuesta (simplificado)

```json
{
  "success": true,
  "period_days": 30,
  "generated_at": "2025-12-29T10:30:00",
  "data": {
    "sales": { /* Todos los datos de sales_data */ },
    "customers": { /* Todos los datos de customer_insights */ },
    "opportunities": { /* Todos los datos de crm_opportunities */ },
    "products": { /* Todos los datos de product_performance */ },
    "team": { /* Todos los datos de sales_team_performance */ },
    "territorial": { /* Todos los datos de territorial_analysis */ },
    "categories": { /* Todos los datos de category_analysis */ }
  },
  "executive_summary": {
    "total_revenue": 1245680.75,
    "num_sales": 892,
    "total_customers": 456,
    "vip_customers": 67,
    "at_risk_customers": 45,
    "new_customers": 28,
    "pipeline_value": 2456789.00,
    "total_opportunities": 89,
    "top_product": "Laptop Dell XPS 15",
    "top_product_revenue": 67500.00,
    "team_size": 8,
    "top_seller": "Carlos Rodríguez",
    "total_states": 15,
    "top_state": "Madrid",
    "top_state_revenue": 345680.50,
    "total_categories": 18,
    "top_category": "CADENA RESTAURANTE",
    "top_category_revenue": 235680.50
  }
}
```

---

## Casos de Uso por Rol

### Director General / CEO

**Herramientas principales:**
- `get_comprehensive_data` - Vista 360° del negocio
- `get_territorial_analysis` - Estrategia de expansión

**Preguntas frecuentes:**
- "¿Cómo está el negocio este mes?"
- "¿Dónde deberíamos expandirnos?"
- "¿Cuál es nuestra tasa de crecimiento?"

### Director Comercial

**Herramientas principales:**
- `get_sales_team_performance` - Gestión del equipo
- `get_crm_opportunities` - Pipeline de ventas
- `get_territorial_analysis` - Asignación de territorios

**Preguntas frecuentes:**
- "¿Quién está cumpliendo objetivos?"
- "¿Cuál es el valor del pipeline?"
- "¿Necesitamos más vendedores en alguna zona?"

### Marketing Manager

**Herramientas principales:**
- `get_customer_insights` - Segmentación de clientes
- `get_product_performance` - Productos a promocionar
- `get_territorial_analysis` - Campañas geográficas

**Preguntas frecuentes:**
- "¿Qué clientes están en riesgo?"
- "¿Qué productos deberíamos promocionar?"
- "¿Dónde invertir en publicidad?"

### Customer Success Manager

**Herramientas principales:**
- `get_customer_insights` (segment: at_risk)
- `search_customers`
- `get_territorial_analysis` (RFM por zona)

**Preguntas frecuentes:**
- "¿Qué clientes necesitan atención urgente?"
- "¿Cuántos clientes VIP tengo?"
- "¿Dónde están concentrados los clientes en riesgo?"

### Vendedor

**Herramientas principales:**
- `search_customers` - Búsqueda rápida
- `get_customer_insights` - Información de clientes
- `get_crm_opportunities` - Mis oportunidades

**Preguntas frecuentes:**
- "¿Cuál es el historial del cliente XYZ?"
- "¿Qué clientes no he contactado en meses?"
- "¿Cuáles son mis mejores clientes?"

### Analista de Datos

**Herramientas principales:**
- Todas las herramientas
- `get_comprehensive_data` para análisis exploratorio

**Preguntas frecuentes:**
- "¿Cuál es la correlación entre X e Y?"
- "¿Hay tendencias estacionales?"
- "¿Qué patrones encontramos en los datos?"

---

## Flujos de Análisis Recomendados

### 1. Análisis Mensual de Negocio

```
1. get_comprehensive_data (days_back: 30)
2. Revisar executive_summary
3. Profundizar en áreas de interés:
   - Si hay problemas de ventas → get_sales_team_performance
   - Si hay clientes en riesgo → get_customer_insights (segment: at_risk)
   - Si hay baja conversión → get_crm_opportunities
```

### 2. Planificación de Expansión Territorial

```
1. get_territorial_analysis (days_back: 90)
2. Identificar provincias de crecimiento alto
3. Analizar expansion_opportunities
4. Revisar rfm_segmentation por zona
5. Evaluar cobertura de vendedores
6. Decisión: ¿Dónde abrir oficina/contratar vendedor?
```

### 3. Campaña de Retención de Clientes

```
1. get_customer_insights (segment: at_risk)
2. Filtrar por provincia objetivo
3. get_territorial_analysis para contexto geográfico
4. Crear lista de contactos prioritarios
5. Diseñar oferta personalizada basada en productos que compraban
```

### 4. Optimización de Inventario

```
1. get_product_performance (days_back: 90, top_n: 50)
2. Identificar productos de alta rotación
3. get_territorial_analysis para ver preferencias por zona
4. Ajustar stock por almacén/tienda según zona
5. Negociar con proveedores de productos top
```

### 5. Evaluación de Equipo Comercial

```
1. get_sales_team_performance (days_back: 30)
2. Comparar con período anterior (days_back: 60)
3. get_crm_opportunities (filtrado por vendedor)
4. Identificar top performers y bajo rendimiento
5. Diseñar plan de acción: coaching, incentivos, redistribución
```

### 6. Análisis de Nuevo Cliente

```
1. search_customers (query: nombre del cliente)
2. Revisar historial de compras
3. Si es prospecto: buscar clientes similares con get_customer_insights
4. Analizar qué productos compran clientes similares
5. Preparar propuesta personalizada
```

---

## Notas Técnicas

### Límites y Optimización

- **Sales Data:** Máximo 1,000 órdenes por llamada
- **Customer Insights:** Máximo 1,000 partners, retorna top 100
- **CRM Opportunities:** Máximo 500 oportunidades
- **Product Performance:** Máximo 5,000 líneas de pedido
- **Territorial Analysis:** Máximo 10,000 órdenes + 20,000 líneas

### Rendimiento

- `search_customers`: ~200-500ms (búsqueda rápida)
- `get_sales_data`: ~1-3 segundos
- `get_customer_insights`: ~5-10 segundos (calcula RFM)
- `get_territorial_analysis`: ~10-20 segundos (análisis exhaustivo)
- `get_comprehensive_data`: ~30-45 segundos (todas las herramientas)

### Autenticación

Todas las herramientas utilizan la misma autenticación XML-RPC configurada en variables de entorno:
- `ODOO_URL`
- `ODOO_DB`
- `ODOO_USERNAME`
- `ODOO_API_KEY`

---

## Glosario de Términos

**RFM:** Recency, Frequency, Monetary - Metodología de segmentación de clientes
**Pipeline:** Conjunto de oportunidades comerciales en curso
**Weighted Pipeline:** Valor del pipeline ajustado por probabilidad de cierre
**LTV (Lifetime Value):** Valor de vida del cliente
**MoM (Month over Month):** Comparación con el mes anterior
**Ticket promedio:** Valor promedio de una venta u orden
**State:** Provincia o estado geográfico en Odoo
**Partner:** Término de Odoo para cliente/contacto/empresa

---

**Versión del documento:** 1.0
**Última actualización:** 2025-12-29
**Versión del MCP Server:** v1.2.0
