"""
Customer Routes - Customer list, detail, graphs, alerts, predictive, environment, and chatbot
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.engines import scoring_engine, graph_engine, alert_engine, summary_engine, chatbot_engine
from backend.engines.scoring_engine import get_risk_bucket, get_customers_by_bucket
from backend.data.simulator import CustomerDataSimulator

router = APIRouter(prefix="/customers", tags=["customers"])
simulator = CustomerDataSimulator()


class ChatRequest(BaseModel):
    query: str


@router.get("")
async def get_customers(segment: str = Query(None, description="Filter by risk segment")):
    """Get list of customers, optionally filtered by risk segment.
    Segment filtering uses model-predicted risk scores."""
    if segment:
        customer_ids = get_customers_by_bucket(segment)
    else:
        customer_ids = simulator.get_customer_list()

    customers = []
    for cid in customer_ids:
        info = simulator.get_customer_info(cid)
        risk = scoring_engine.calculate_risk_score(cid)
        elasticity = scoring_engine.calculate_elasticity_score(cid)
        alerts = alert_engine.get_customer_alerts(cid)

        trend_raw = info.get('risk_trend', 'stable')
        trend_arrow = '→'
        if trend_raw in ('increasing', 'high', 'critical'):
            trend_arrow = '↑'
        elif trend_raw == 'decreasing':
            trend_arrow = '↓'

        last_alert = alerts[0]['message'] if alerts else 'None'

        customers.append({
            "id": cid,
            "name": info.get('name', 'Unknown'),
            "risk_score": round(risk * 100, 1),
            "elasticity_score": round(elasticity, 2),
            "last_alert": last_alert,
            "trend": trend_arrow,
            "risk_bucket": get_risk_bucket(risk)
        })

    return customers


@router.get("/{customer_id}")
async def get_customer_detail(customer_id: str):
    """Get detailed customer profile."""
    info = simulator.get_customer_info(customer_id)
    if not info:
        return {"error": "Customer not found"}

    risk = scoring_engine.calculate_risk_score(customer_id)
    elasticity = scoring_engine.calculate_elasticity_score(customer_id)
    trend = info.get('risk_trend', 'stable')

    return {
        "id": customer_id,
        "name": info.get('name', 'Unknown'),
        "location": info.get('environment', 'N/A'),
        "income_stability": info.get('income_stability', 'N/A'),
        "risk_score": round(risk * 100, 1),
        "elasticity_score": round(elasticity, 2),
        "risk_bucket": scoring_engine.get_risk_bucket(risk),
        "risk_trend": trend,
        "risk_class": scoring_engine.get_risk_class_label(risk, trend),
        "insights": simulator.get_environment_insights(customer_id)
    }


@router.get("/{customer_id}/graphs")
async def get_customer_graphs(customer_id: str):
    """Get all graph data for a customer."""
    return graph_engine.get_all_graphs(customer_id)


@router.get("/{customer_id}/alerts")
async def get_customer_alerts_route(customer_id: str):
    """Get all active alerts for a customer."""
    alerts = alert_engine.get_customer_alerts(customer_id)
    return alert_engine.prioritize_alerts(alerts)


@router.get("/{customer_id}/summary")
async def get_customer_summary(customer_id: str):
    """Get today's comprehensive summary for a customer."""
    return summary_engine.get_todays_summary(customer_id)


@router.get("/{customer_id}/predictive")
async def get_predictive_analytics(customer_id: str):
    """Get predictive forecast for next 2-4 weeks."""
    return scoring_engine.get_predictive_forecast(customer_id)


@router.get("/{customer_id}/environment")
async def get_environment_analysis(customer_id: str):
    """Get environment-aware analysis data."""
    return graph_engine.generate_environment_data(customer_id)


@router.get("/{customer_id}/failed-payments")
async def get_failed_payments(customer_id: str):
    """Get failed payments timeline and rolling frequency."""
    return graph_engine.generate_failed_payments_timeline(customer_id)


@router.post("/{customer_id}/chat")
async def chat_with_customer(customer_id: str, request: ChatRequest):
    """Process a chatbot query for a customer."""
    return chatbot_engine.process_query(customer_id, request.query)
