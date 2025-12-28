# odoo_mcp_api.py - VERSIÓN CON ANÁLISIS TERRITORIAL EXHAUSTIVO v1.2.0
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import xmlrpc.client
import json
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Odoo MCP Server for Claude",
    description="Marketing & Sales Manager AI - Odoo Data Access with Enhanced Territorial Analysis",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OdooConnector:
    def __init__(self):
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USERNAME')
        self.api_key = os.getenv('ODOO_API_KEY')
        self.uid = None
        self.models = None
        logger.info(f"🔧 Initializing Odoo connector for {self.url}")

    def authenticate(self):
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.api_key, {})
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            logger.info(f"✅ Authenticated with Odoo - UID: {self.uid}")
            return self.uid
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None):
        if not self.uid:
            self.authenticate()
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.api_key,
                model, method, args, kwargs or {}
            )
            logger.info(f"📊 Executed {model}.{method} - Returned {len(result) if isinstance(result, list) else 1} records")
            return result
        except Exception as e:
            logger.error(f"❌ Error executing {model}.{method}: {e}")
            raise

# Inicializar conector global
odoo = OdooConnector()

# ==================== MODELOS PYDANTIC ====================

class SalesDataRequest(BaseModel):
    days_back: int = 30
    state: Optional[str] = None
    partner_ids: Optional[List[int]] = None
    min_amount: Optional[float] = None

class CustomerInsightsRequest(BaseModel):
    segment: str = "all"  # all, vip, at_risk, new, inactive, regular
    min_purchases: Optional[int] = None
    min_revenue: Optional[float] = None

class OpportunitiesRequest(BaseModel):
    stage: Optional[str] = None
    min_probability: Optional[int] = None
    days_inactive: Optional[int] = None

class ProductPerformanceRequest(BaseModel):
    days_back: int = 90
    top_n: int = 20

class CustomerSearchRequest(BaseModel):
    query: str
    limit: int = 10

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "service": "Odoo MCP Server for Claude",
        "status": "running",
        "description": "Marketing & Sales Manager AI - Odoo Data Access with Enhanced Territorial Analysis",
        "version": "1.2.0",
        "endpoints": {
            "health": "GET /health - Check server health and Odoo connection",
            "tools": "GET /tools - List all available tools",
            "sales": "POST /get_sales_data - Get sales orders with filters",
            "customers": "POST /get_customer_insights - Customer segmentation (RFM analysis) with geographic data",
            "opportunities": "POST /get_crm_opportunities - CRM pipeline data",
            "products": "POST /get_product_performance - Product sales performance",
            "team": "POST /get_sales_team_performance - Sales team metrics",
            "search": "POST /search_customers - Search customers by name/email/phone with geographic data",
            "territorial": "POST /get_territorial_analysis - Territorial analysis by province/city",
            "comprehensive": "POST /get_comprehensive_data - All data for complete analysis"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        if not odoo.uid:
            odoo.authenticate()
        return {
            "status": "healthy",
            "odoo_connected": True,
            "odoo_uid": odoo.uid,
            "odoo_url": odoo.url,
            "odoo_db": odoo.db,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "odoo_connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/tools")
async def list_tools():
    """Lista todas las herramientas disponibles para Claude"""
    return {
        "tools": [
            {
                "name": "get_sales_data",
                "description": "Obtiene datos de ventas con filtros opcionales",
                "parameters": ["days_back", "state", "partner_ids", "min_amount"]
            },
            {
                "name": "get_customer_insights",
                "description": "Analiza comportamiento y segmentación de clientes (RFM) con datos geográficos completos (state_id, city, zip, etc.)",
                "parameters": ["segment", "min_purchases", "min_revenue"]
            },
            {
                "name": "get_crm_opportunities",
                "description": "Obtiene oportunidades del pipeline de ventas",
                "parameters": ["stage", "min_probability", "days_inactive"]
            },
            {
                "name": "get_product_performance",
                "description": "Analiza rendimiento de productos por ventas",
                "parameters": ["days_back", "top_n"]
            },
            {
                "name": "get_sales_team_performance",
                "description": "Métricas de rendimiento del equipo de ventas",
                "parameters": ["days_back"]
            },
            {
                "name": "search_customers",
                "description": "Busca clientes por nombre, email o teléfono con datos geográficos completos (state_id, city, zip, street, vat, etc.)",
                "parameters": ["query", "limit"]
            },
            {
                "name": "get_territorial_analysis",
                "description": "Análisis territorial EXHAUSTIVO v1.2.0: clientes, ventas, productos y vendedores por provincia/ciudad. NUEVAS FUNCIONALIDADES: segmentación RFM territorial, análisis MoM (comparación con período anterior), métricas de concentración, y oportunidades de expansión.",
                "parameters": ["days_back"]
            },
            {
                "name": "get_comprehensive_data",
                "description": "Obtiene todos los datos necesarios para análisis completo",
                "parameters": ["days_back"]
            }
        ]
    }

@app.post("/get_sales_data")
async def get_sales_data(request: SalesDataRequest):
    """Obtiene datos de ventas de Odoo con filtros opcionales"""
    try:
        date_from = (datetime.now() - timedelta(days=request.days_back)).strftime('%Y-%m-%d')

        filters = [['date_order', '>=', date_from]]

        if request.state:
            filters.append(['state', '=', request.state])
        if request.partner_ids:
            filters.append(['partner_id', 'in', request.partner_ids])
        if request.min_amount:
            filters.append(['amount_total', '>=', request.min_amount])

        sales = odoo.execute_kw('sale.order', 'search_read', [filters], {
            'fields': ['name', 'partner_id', 'date_order', 'amount_total',
                      'state', 'user_id', 'team_id'],
            'order': 'date_order desc',
            'limit': 1000
        })

        # Calcular estadísticas
        total_revenue = sum(s.get('amount_total', 0) for s in sales)
        avg_order = total_revenue / len(sales) if sales else 0

        return {
            "success": True,
            "count": len(sales),
            "data": sales,
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "avg_order_value": round(avg_order, 2),
                "period_days": request.days_back,
                "date_from": date_from,
                "date_to": datetime.now().strftime('%Y-%m-%d')
            }
        }
    except Exception as e:
        logger.error(f"Error in get_sales_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_customer_insights")
async def get_customer_insights(request: CustomerInsightsRequest):
    """Analiza comportamiento y segmentación RFM de clientes - INCLUYE DATOS GEOGRÁFICOS"""
    try:
        partners = odoo.execute_kw('res.partner', 'search_read',
            [[['customer_rank', '>', 0]]], {
            'fields': ['name', 'email', 'phone', 'mobile', 'street', 'street2',
                      'city', 'state_id', 'zip', 'country_id', 'vat',
                      'create_date', 'ref'],
            'limit': 1000
        })

        insights = []
        for partner in partners:
            # Obtener órdenes del cliente
            orders = odoo.execute_kw('sale.order', 'search_read',
                [[['partner_id', '=', partner['id']], ['state', 'in', ['sale', 'done']]]], {
                'fields': ['date_order', 'amount_total']
            })

            if orders:
                total_revenue = sum(o['amount_total'] for o in orders)
                num_purchases = len(orders)
                last_order_date = max(o['date_order'] for o in orders)
                days_since_last = (datetime.now() - datetime.strptime(last_order_date[:10], '%Y-%m-%d')).days

                # Segmentación RFM
                if total_revenue > 10000 and num_purchases > 5:
                    segment = "vip"
                elif days_since_last > 180 and num_purchases > 2:
                    segment = "at_risk"
                elif num_purchases == 1 and days_since_last < 30:
                    segment = "new"
                elif days_since_last > 365:
                    segment = "inactive"
                else:
                    segment = "regular"

                # Filtrar por segmento solicitado
                if request.segment == "all" or request.segment == segment:
                    insight = {
                        'partner_id': partner['id'],
                        'name': partner['name'],
                        'email': partner['email'],
                        'phone': partner['phone'],
                        'mobile': partner.get('mobile'),
                        'street': partner.get('street'),
                        'street2': partner.get('street2'),
                        'city': partner.get('city'),
                        'state_id': partner.get('state_id'),
                        'zip': partner.get('zip'),
                        'country_id': partner.get('country_id'),
                        'vat': partner.get('vat'),
                        'ref': partner.get('ref'),
                        'total_revenue': round(total_revenue, 2),
                        'num_purchases': num_purchases,
                        'avg_order_value': round(total_revenue / num_purchases, 2),
                        'last_order_date': last_order_date,
                        'days_since_last': days_since_last,
                        'segment': segment,
                        'customer_since': partner['create_date'],
                        'ltv_score': round(total_revenue * (1 - min(days_since_last / 365, 1)), 2)
                    }

                    # Aplicar filtros adicionales
                    if request.min_purchases and insight['num_purchases'] < request.min_purchases:
                        continue
                    if request.min_revenue and insight['total_revenue'] < request.min_revenue:
                        continue

                    insights.append(insight)

        # Ordenar por revenue
        insights.sort(key=lambda x: x['total_revenue'], reverse=True)

        return {
            "success": True,
            "count": len(insights),
            "data": insights[:100],  # Limitar a top 100
            "summary": {
                "segments": {
                    "vip": len([c for c in insights if c['segment'] == 'vip']),
                    "regular": len([c for c in insights if c['segment'] == 'regular']),
                    "at_risk": len([c for c in insights if c['segment'] == 'at_risk']),
                    "new": len([c for c in insights if c['segment'] == 'new']),
                    "inactive": len([c for c in insights if c['segment'] == 'inactive'])
                },
                "total_revenue": round(sum(c['total_revenue'] for c in insights), 2),
                "avg_revenue_per_customer": round(sum(c['total_revenue'] for c in insights) / len(insights), 2) if insights else 0
            }
        }
    except Exception as e:
        logger.error(f"Error in get_customer_insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_crm_opportunities")
async def get_crm_opportunities(request: OpportunitiesRequest):
    """Obtiene y analiza oportunidades del CRM"""
    try:
        filters = []

        if request.stage:
            filters.append(['stage_id.name', '=', request.stage])
        if request.min_probability is not None:
            filters.append(['probability', '>=', request.min_probability])
        if request.days_inactive:
            date_limit = (datetime.now() - timedelta(days=request.days_inactive)).strftime('%Y-%m-%d')
            filters.append(['write_date', '<', date_limit])

        opportunities = odoo.execute_kw('crm.lead', 'search_read', [filters], {
            'fields': ['name', 'partner_id', 'expected_revenue', 'probability',
                      'stage_id', 'user_id', 'team_id', 'date_deadline',
                      'create_date', 'write_date'],
            'order': 'expected_revenue desc',
            'limit': 500
        })

        # Calcular métricas del pipeline
        total_pipeline = sum(o.get('expected_revenue', 0) or 0 for o in opportunities)
        weighted_pipeline = sum(
            (o.get('expected_revenue', 0) or 0) * (o.get('probability', 0) or 0) / 100
            for o in opportunities
        )

        return {
            "success": True,
            "count": len(opportunities),
            "data": opportunities,
            "pipeline_metrics": {
                "total_opportunities": len(opportunities),
                "total_pipeline_value": round(total_pipeline, 2),
                "weighted_pipeline_value": round(weighted_pipeline, 2),
                "avg_deal_size": round(total_pipeline / len(opportunities), 2) if opportunities else 0,
                "avg_probability": round(sum(o.get('probability', 0) or 0 for o in opportunities) / len(opportunities), 2) if opportunities else 0
            }
        }
    except Exception as e:
        logger.error(f"Error in get_crm_opportunities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_product_performance")
async def get_product_performance(request: ProductPerformanceRequest):
    """Analiza rendimiento de productos - VERSIÓN CORREGIDA"""
    try:
        date_from = (datetime.now() - timedelta(days=request.days_back)).strftime('%Y-%m-%d')

        order_lines = odoo.execute_kw('sale.order.line', 'search_read',
            [[['order_id.date_order', '>=', date_from], ['order_id.state', 'in', ['sale', 'done']]]], {
            'fields': ['product_id', 'product_uom_qty', 'price_subtotal'],
            'limit': 5000
        })

        product_stats = {}
        skipped_lines = 0

        for line in order_lines:
            # FIX: Verificar que product_id no sea False o None
            if not line.get('product_id') or line['product_id'] is False:
                skipped_lines += 1
                continue

            prod_id = line['product_id'][0]
            if prod_id not in product_stats:
                product_stats[prod_id] = {
                    'product_name': line['product_id'][1],
                    'total_qty': 0,
                    'total_revenue': 0
                }

            product_stats[prod_id]['total_qty'] += line.get('product_uom_qty', 0)
            product_stats[prod_id]['total_revenue'] += line.get('price_subtotal', 0)

        if skipped_lines > 0:
            logger.warning(f"Skipped {skipped_lines} order lines without product_id")

        # Convertir a lista
        performance = [
            {
                'product_id': pid,
                'product_name': stats['product_name'],
                'total_qty_sold': stats['total_qty'],
                'total_revenue': round(stats['total_revenue'], 2)
            }
            for pid, stats in product_stats.items()
        ]

        # Ordenar por revenue y limitar
        performance.sort(key=lambda x: x['total_revenue'], reverse=True)

        return {
            "success": True,
            "count": len(performance),
            "data": performance[:request.top_n],
            "summary": {
                "total_products": len(performance),
                "total_revenue": round(sum(p['total_revenue'] for p in performance), 2),
                "period_days": request.days_back,
                "skipped_lines": skipped_lines
            }
        }
    except Exception as e:
        logger.error(f"Error in get_product_performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_sales_team_performance")
async def get_sales_team_performance(request: SalesDataRequest):
    """Analiza rendimiento del equipo de ventas"""
    try:
        date_from = (datetime.now() - timedelta(days=request.days_back)).strftime('%Y-%m-%d')

        sales = odoo.execute_kw('sale.order', 'search_read',
            [[['date_order', '>=', date_from], ['state', 'in', ['sale', 'done']]]], {
            'fields': ['user_id', 'amount_total']
        })

        team_stats = {}
        for sale in sales:
            if sale.get('user_id'):
                user_id = sale['user_id'][0]
                if user_id not in team_stats:
                    team_stats[user_id] = {
                        'user_name': sale['user_id'][1],
                        'total_revenue': 0,
                        'num_deals': 0
                    }
                team_stats[user_id]['total_revenue'] += sale['amount_total']
                team_stats[user_id]['num_deals'] += 1

        # Calcular métricas
        performance = [
            {
                'user_id': uid,
                'user_name': stats['user_name'],
                'total_revenue': round(stats['total_revenue'], 2),
                'num_deals': stats['num_deals'],
                'avg_deal_size': round(stats['total_revenue'] / stats['num_deals'], 2)
            }
            for uid, stats in team_stats.items()
        ]

        performance.sort(key=lambda x: x['total_revenue'], reverse=True)

        return {
            "success": True,
            "count": len(performance),
            "data": performance,
            "team_summary": {
                "total_revenue": round(sum(p['total_revenue'] for p in performance), 2),
                "total_deals": sum(p['num_deals'] for p in performance),
                "avg_deal_size": round(sum(p['total_revenue'] for p in performance) / sum(p['num_deals'] for p in performance), 2) if performance else 0,
                "period_days": request.days_back
            }
        }
    except Exception as e:
        logger.error(f"Error in get_sales_team_performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_customers")
async def search_customers(request: CustomerSearchRequest):
    """Busca clientes por nombre, email o teléfono - INCLUYE DATOS GEOGRÁFICOS"""
    try:
        filters = [
            '|', '|', '|',
            ['name', 'ilike', request.query],
            ['email', 'ilike', request.query],
            ['phone', 'ilike', request.query],
            ['ref', 'ilike', request.query]
        ]

        customers = odoo.execute_kw('res.partner', 'search_read', [filters], {
            'fields': ['name', 'email', 'phone', 'mobile', 'street', 'street2',
                      'city', 'state_id', 'zip', 'country_id', 'vat',
                      'customer_rank', 'supplier_rank', 'sale_order_count',
                      'create_date', 'write_date', 'ref', 'comment'],
            'limit': request.limit
        })

        return {
            "success": True,
            "count": len(customers),
            "data": customers,
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Error in search_customers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_territorial_analysis")
async def get_territorial_analysis(request: SalesDataRequest):
    """
    Análisis territorial EXHAUSTIVO: clientes, ventas, productos y vendedores por provincia/ciudad.

    NUEVAS FUNCIONALIDADES v1.2.0:
    - Segmentación RFM por territorio
    - Análisis temporal (comparación con período anterior)
    - Métricas de concentración y distribución
    - Análisis de oportunidades y potencial de crecimiento
    """
    try:
        date_from = (datetime.now() - timedelta(days=request.days_back)).strftime('%Y-%m-%d')
        date_from_previous = (datetime.now() - timedelta(days=request.days_back * 2)).strftime('%Y-%m-%d')
        date_to_previous = (datetime.now() - timedelta(days=request.days_back + 1)).strftime('%Y-%m-%d')

        # 1. Obtener todos los clientes con datos geográficos
        logger.info("📍 Fetching customers with geographic data...")
        customers = odoo.execute_kw('res.partner', 'search_read',
            [[['customer_rank', '>', 0]]], {
            'fields': ['id', 'name', 'city', 'state_id', 'country_id'],
            'limit': 5000
        })

        # 2. Obtener ventas del período ACTUAL con partner info
        logger.info(f"📊 Fetching sales from {date_from}...")
        sales = odoo.execute_kw('sale.order', 'search_read',
            [[['date_order', '>=', date_from], ['state', 'in', ['sale', 'done']]]], {
            'fields': ['partner_id', 'amount_total', 'user_id', 'date_order'],
            'limit': 10000
        })

        # 2b. Obtener ventas del período ANTERIOR para comparación temporal
        logger.info(f"📊 Fetching previous period sales ({date_from_previous} to {date_to_previous})...")
        sales_previous = odoo.execute_kw('sale.order', 'search_read',
            [[['date_order', '>=', date_from_previous], ['date_order', '<=', date_to_previous], ['state', 'in', ['sale', 'done']]]], {
            'fields': ['partner_id', 'amount_total'],
            'limit': 10000
        })

        # 2c. Obtener TODAS las órdenes de clientes para segmentación RFM
        logger.info("👥 Fetching all customer orders for RFM segmentation...")
        all_customer_orders = odoo.execute_kw('sale.order', 'search_read',
            [[['state', 'in', ['sale', 'done']]]], {
            'fields': ['partner_id', 'amount_total', 'date_order'],
            'limit': 20000
        })

        # 3. Obtener líneas de pedido para análisis de productos por territorio
        logger.info("🎯 Fetching order lines for product analysis...")
        order_ids = [s['id'] for s in sales]
        if order_ids:
            order_lines = odoo.execute_kw('sale.order.line', 'search_read',
                [[['order_id', 'in', order_ids]]], {
                'fields': ['order_id', 'product_id', 'product_uom_qty', 'price_subtotal'],
                'limit': 20000
            })
        else:
            order_lines = []

        # 4. Crear mapeo de clientes a ubicación
        customer_location = {}
        for customer in customers:
            customer_location[customer['id']] = {
                'name': customer['name'],
                'city': customer.get('city', 'Sin ciudad'),
                'state': customer.get('state_id', [False, 'Sin provincia'])[1] if customer.get('state_id') else 'Sin provincia',
                'state_id': customer.get('state_id', [False])[0] if customer.get('state_id') else None,
                'country': customer.get('country_id', [False, 'Sin país'])[1] if customer.get('country_id') else 'Sin país'
            }

        # 5. Agregar datos por provincia
        territorial_data = {}

        for sale in sales:
            partner_id = sale['partner_id'][0] if sale.get('partner_id') else None
            if not partner_id or partner_id not in customer_location:
                continue

            location = customer_location[partner_id]
            state = location['state']
            city = location['city']

            # Inicializar provincia si no existe
            if state not in territorial_data:
                territorial_data[state] = {
                    'state': state,
                    'total_revenue': 0,
                    'num_orders': 0,
                    'customers': set(),
                    'cities': {},
                    'salespeople': {},
                    'products': {}
                }

            # Agregar datos de venta
            territorial_data[state]['total_revenue'] += sale.get('amount_total', 0)
            territorial_data[state]['num_orders'] += 1
            territorial_data[state]['customers'].add(partner_id)

            # Agregar datos por ciudad
            if city not in territorial_data[state]['cities']:
                territorial_data[state]['cities'][city] = {
                    'revenue': 0,
                    'orders': 0,
                    'customers': set()
                }
            territorial_data[state]['cities'][city]['revenue'] += sale.get('amount_total', 0)
            territorial_data[state]['cities'][city]['orders'] += 1
            territorial_data[state]['cities'][city]['customers'].add(partner_id)

            # Agregar datos de vendedores
            if sale.get('user_id'):
                user_name = sale['user_id'][1]
                if user_name not in territorial_data[state]['salespeople']:
                    territorial_data[state]['salespeople'][user_name] = {
                        'revenue': 0,
                        'orders': 0
                    }
                territorial_data[state]['salespeople'][user_name]['revenue'] += sale.get('amount_total', 0)
                territorial_data[state]['salespeople'][user_name]['orders'] += 1

        # 6. Agregar productos por territorio
        order_to_partner = {s['id']: s['partner_id'][0] if s.get('partner_id') else None for s in sales}

        for line in order_lines:
            if not line.get('product_id'):
                continue

            order_id = line['order_id'][0] if line.get('order_id') else None
            if not order_id or order_id not in order_to_partner:
                continue

            partner_id = order_to_partner[order_id]
            if not partner_id or partner_id not in customer_location:
                continue

            state = customer_location[partner_id]['state']
            if state not in territorial_data:
                continue

            product_name = line['product_id'][1]
            if product_name not in territorial_data[state]['products']:
                territorial_data[state]['products'][product_name] = {
                    'qty': 0,
                    'revenue': 0
                }

            territorial_data[state]['products'][product_name]['qty'] += line.get('product_uom_qty', 0)
            territorial_data[state]['products'][product_name]['revenue'] += line.get('price_subtotal', 0)

        # 7. Calcular segmentación RFM por cliente
        logger.info("🎯 Calculating RFM segmentation...")
        customer_rfm = {}
        for order in all_customer_orders:
            partner_id = order['partner_id'][0] if order.get('partner_id') else None
            if not partner_id:
                continue

            if partner_id not in customer_rfm:
                customer_rfm[partner_id] = {
                    'total_revenue': 0,
                    'num_purchases': 0,
                    'last_order_date': None
                }

            customer_rfm[partner_id]['total_revenue'] += order.get('amount_total', 0)
            customer_rfm[partner_id]['num_purchases'] += 1
            order_date = order.get('date_order', '')
            if order_date:
                if not customer_rfm[partner_id]['last_order_date'] or order_date > customer_rfm[partner_id]['last_order_date']:
                    customer_rfm[partner_id]['last_order_date'] = order_date

        # Asignar segmento RFM a cada cliente
        for partner_id, metrics in customer_rfm.items():
            if metrics['last_order_date']:
                days_since_last = (datetime.now() - datetime.strptime(metrics['last_order_date'][:10], '%Y-%m-%d')).days
            else:
                days_since_last = 999

            total_revenue = metrics['total_revenue']
            num_purchases = metrics['num_purchases']

            # Segmentación RFM
            if total_revenue > 10000 and num_purchases > 5:
                segment = "vip"
            elif days_since_last > 180 and num_purchases > 2:
                segment = "at_risk"
            elif num_purchases == 1 and days_since_last < 30:
                segment = "new"
            elif days_since_last > 365:
                segment = "inactive"
            else:
                segment = "regular"

            customer_rfm[partner_id]['segment'] = segment

        # 8. Calcular métricas del período anterior por provincia
        logger.info("📈 Calculating previous period metrics...")
        previous_revenue_by_state = {}
        for sale in sales_previous:
            partner_id = sale['partner_id'][0] if sale.get('partner_id') else None
            if not partner_id or partner_id not in customer_location:
                continue

            state = customer_location[partner_id]['state']
            if state not in previous_revenue_by_state:
                previous_revenue_by_state[state] = 0
            previous_revenue_by_state[state] += sale.get('amount_total', 0)

        # 9. Formatear resultados
        results = []
        for state, data in territorial_data.items():
            # Top 5 ciudades
            cities_sorted = sorted(
                [{'city': city, **stats, 'num_customers': len(stats['customers'])}
                 for city, stats in data['cities'].items()],
                key=lambda x: x['revenue'],
                reverse=True
            )

            # Top 5 productos
            products_sorted = sorted(
                [{'product': prod, **stats} for prod, stats in data['products'].items()],
                key=lambda x: x['revenue'],
                reverse=True
            )

            # Top vendedores
            salespeople_sorted = sorted(
                [{'salesperson': name, **stats} for name, stats in data['salespeople'].items()],
                key=lambda x: x['revenue'],
                reverse=True
            )

            # Calcular segmentación RFM por territorio
            rfm_segments = {'vip': 0, 'at_risk': 0, 'new': 0, 'inactive': 0, 'regular': 0}
            for customer_id in data['customers']:
                if customer_id in customer_rfm:
                    segment = customer_rfm[customer_id].get('segment', 'regular')
                    rfm_segments[segment] += 1

            # Calcular crecimiento vs período anterior
            current_revenue = data['total_revenue']
            previous_revenue = previous_revenue_by_state.get(state, 0)
            if previous_revenue > 0:
                growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
            else:
                growth_rate = 100 if current_revenue > 0 else 0

            # Métricas de concentración
            total_cities_revenue = sum(c['revenue'] for c in cities_sorted)
            top3_cities_revenue = sum(c['revenue'] for c in cities_sorted[:3])
            concentration_index = (top3_cities_revenue / total_cities_revenue * 100) if total_cities_revenue > 0 else 0

            # Análisis de oportunidades
            cities_with_few_customers = [c for c in cities_sorted if c['num_customers'] <= 2 and c['num_customers'] > 0]
            expansion_opportunities = len(cities_with_few_customers)

            results.append({
                'state': state,
                'total_revenue': round(data['total_revenue'], 2),
                'num_orders': data['num_orders'],
                'num_customers': len(data['customers']),
                'avg_order_value': round(data['total_revenue'] / data['num_orders'], 2) if data['num_orders'] > 0 else 0,
                'top_cities': cities_sorted[:5],
                'top_products': products_sorted[:5],
                'salespeople': salespeople_sorted,
                # NUEVAS MÉTRICAS
                'rfm_segmentation': rfm_segments,
                'growth_vs_previous_period': {
                    'current_revenue': round(current_revenue, 2),
                    'previous_revenue': round(previous_revenue, 2),
                    'growth_rate': round(growth_rate, 2),
                    'growth_amount': round(current_revenue - previous_revenue, 2)
                },
                'concentration_metrics': {
                    'total_cities': len(cities_sorted),
                    'top3_concentration_pct': round(concentration_index, 2)
                },
                'expansion_opportunities': {
                    'cities_with_1_2_customers': expansion_opportunities,
                    'potential_cities': cities_with_few_customers[:5]
                }
            })

        # Ordenar por revenue
        results.sort(key=lambda x: x['total_revenue'], reverse=True)

        total_revenue = sum(r['total_revenue'] for r in results)
        total_previous_revenue = sum(previous_revenue_by_state.values())

        # Agregar métricas globales de RFM
        global_rfm = {'vip': 0, 'at_risk': 0, 'new': 0, 'inactive': 0, 'regular': 0}
        for r in results:
            for segment, count in r['rfm_segmentation'].items():
                global_rfm[segment] += count

        # Calcular total de ciudades y oportunidades de expansión
        total_cities = sum(r['concentration_metrics']['total_cities'] for r in results)
        total_expansion_opportunities = sum(r['expansion_opportunities']['cities_with_1_2_customers'] for r in results)

        # Crecimiento global
        global_growth_rate = 0
        if total_previous_revenue > 0:
            global_growth_rate = ((total_revenue - total_previous_revenue) / total_previous_revenue) * 100

        # Top territorios de crecimiento
        growing_states = [r for r in results if r['growth_vs_previous_period']['growth_rate'] > 0]
        growing_states_sorted = sorted(growing_states, key=lambda x: x['growth_vs_previous_period']['growth_rate'], reverse=True)

        return {
            "success": True,
            "count": len(results),
            "data": results,
            "summary": {
                # Métricas básicas
                "total_revenue": round(total_revenue, 2),
                "total_states": len(results),
                "total_orders": sum(r['num_orders'] for r in results),
                "total_customers": sum(r['num_customers'] for r in results),
                "total_cities": total_cities,
                "period_days": request.days_back,
                "date_from": date_from,
                "date_to": datetime.now().strftime('%Y-%m-%d'),
                "top_state": results[0]['state'] if results else None,
                "top_state_revenue": results[0]['total_revenue'] if results else 0,
                # NUEVAS MÉTRICAS AGREGADAS
                "global_rfm_segmentation": global_rfm,
                "global_growth": {
                    "current_period_revenue": round(total_revenue, 2),
                    "previous_period_revenue": round(total_previous_revenue, 2),
                    "growth_rate_pct": round(global_growth_rate, 2),
                    "growth_amount": round(total_revenue - total_previous_revenue, 2)
                },
                "top_growing_states": [
                    {
                        "state": s['state'],
                        "growth_rate": s['growth_vs_previous_period']['growth_rate'],
                        "revenue": s['total_revenue']
                    } for s in growing_states_sorted[:5]
                ],
                "expansion_insights": {
                    "total_expansion_opportunities": total_expansion_opportunities,
                    "states_with_high_concentration": len([r for r in results if r['concentration_metrics']['top3_concentration_pct'] > 80]),
                    "underserved_territories": len([r for r in results if r['num_customers'] < 5])
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in get_territorial_analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_comprehensive_data")
async def get_comprehensive_data(request: SalesDataRequest):
    """
    Endpoint especial que obtiene TODOS los datos necesarios para análisis completo.
    Ideal para que Claude haga análisis profundos con una sola llamada.
    """
    try:
        logger.info(f"📊 Getting comprehensive data for last {request.days_back} days")

        # Preparar requests
        sales_req = SalesDataRequest(days_back=request.days_back)
        customer_req = CustomerInsightsRequest(segment="all")
        opp_req = OpportunitiesRequest()
        product_req = ProductPerformanceRequest(days_back=request.days_back)

        # Obtener todos los datos
        sales_data = await get_sales_data(sales_req)
        customer_data = await get_customer_insights(customer_req)
        opp_data = await get_crm_opportunities(opp_req)
        product_data = await get_product_performance(product_req)
        team_data = await get_sales_team_performance(sales_req)
        territorial_data = await get_territorial_analysis(sales_req)

        return {
            "success": True,
            "period_days": request.days_back,
            "generated_at": datetime.now().isoformat(),
            "data": {
                "sales": sales_data,
                "customers": customer_data,
                "opportunities": opp_data,
                "products": product_data,
                "team": team_data,
                "territorial": territorial_data
            },
            "executive_summary": {
                "total_revenue": sales_data["summary"]["total_revenue"],
                "num_sales": sales_data["count"],
                "total_customers": customer_data["count"],
                "vip_customers": customer_data["summary"]["segments"]["vip"],
                "at_risk_customers": customer_data["summary"]["segments"]["at_risk"],
                "new_customers": customer_data["summary"]["segments"]["new"],
                "pipeline_value": opp_data["pipeline_metrics"]["weighted_pipeline_value"],
                "total_opportunities": opp_data["count"],
                "top_product": product_data["data"][0]["product_name"] if product_data["data"] else "N/A",
                "top_product_revenue": product_data["data"][0]["total_revenue"] if product_data["data"] else 0,
                "team_size": team_data["count"],
                "top_seller": team_data["data"][0]["user_name"] if team_data["data"] else "N/A",
                "total_states": territorial_data["summary"]["total_states"],
                "top_state": territorial_data["summary"]["top_state"],
                "top_state_revenue": territorial_data["summary"]["top_state_revenue"]
            }
        }
    except Exception as e:
        logger.error(f"Error in get_comprehensive_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    # Autenticar al inicio
    try:
        odoo.authenticate()
    except Exception as e:
        logger.error(f"⚠️  Failed to authenticate on startup: {e}")

    # Iniciar servidor
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
