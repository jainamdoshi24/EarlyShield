"""
Segment Routes - Risk segment listing and filtering.

All segment counts and customer assignments use model-predicted risk scores
(via scoring_engine), NOT the hardcoded base_risk.
"""
from fastapi import APIRouter
from backend.engines.scoring_engine import (
    get_risk_segment_counts,
    get_customers_by_bucket,
    calculate_risk_score,
    calculate_elasticity_score,
    get_risk_bucket,
)
from backend.engines.alert_engine import get_customer_alerts
from backend.data.simulator import CustomerDataSimulator

router = APIRouter(prefix="/segments", tags=["segments"])
simulator = CustomerDataSimulator()

SEGMENT_LABELS = {
    '0-20%': '0–20% Low Delinquent',
    '20-40%': '20–40% Moderate Delinquent',
    '40-60%': '40–60% Delinquent',
    '60-80%': '60–80% High Risk',
    '80%+': '80%+ Extremely High'
}


@router.get("")
async def list_segments():
    """List all risk segments with their counts and labels.
    Counts are based on model-predicted risk scores."""
    counts = get_risk_segment_counts()
    segments = []
    for bucket, count in counts.items():
        segments.append({
            "bucket": bucket,
            "label": SEGMENT_LABELS.get(bucket, bucket),
            "count": count
        })
    return segments


@router.get("/{bucket}/customers")
async def get_segment_customers(bucket: str):
    """Get customers in a specific risk segment.
    Assignments are based on model-predicted risk scores."""
    customer_ids = get_customers_by_bucket(bucket)
    customers = []
    for cid in customer_ids:
        info = simulator.get_customer_info(cid)
        risk = calculate_risk_score(cid)
        elasticity = calculate_elasticity_score(cid)
        alerts = get_customer_alerts(cid)

        # Map trend to arrow
        trend_raw = info.get('risk_trend', 'stable')
        trend_arrow = '→'
        if trend_raw in ('increasing', 'high', 'critical'):
            trend_arrow = '↑'
        elif trend_raw == 'decreasing':
            trend_arrow = '↓'

        # Last alert
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
