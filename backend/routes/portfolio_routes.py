"""
Portfolio Routes - KPIs, distribution, and three landing-page chart endpoints
"""
from fastapi import APIRouter
from backend.engines import scoring_engine

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

SEGMENT_LABELS = {
    '0-20%': '0–20% Low Delinquent',
    '20-40%': '20–40% Moderate Delinquent',
    '40-60%': '40–60% Delinquent',
    '60-80%': '60–80% High Risk',
    '80%+': '80%+ Extremely High'
}

SEGMENT_COLORS = {
    '0-20%': '#22c55e',
    '20-40%': '#3b82f6',
    '40-60%': '#f59e0b',
    '60-80%': '#f97316',
    '80%+': '#ef4444'
}


@router.get("/segments")
async def get_segments():
    """Get count of customers in each risk segment."""
    return scoring_engine.get_risk_segment_counts()


@router.get("/distribution")
async def get_distribution():
    """Get risk distribution data for donut chart."""
    counts = scoring_engine.get_risk_segment_counts()
    return {
        "labels": [SEGMENT_LABELS.get(k, k) for k in counts.keys()],
        "values": list(counts.values()),
        "colors": [SEGMENT_COLORS.get(k, '#888') for k in counts.keys()],
        "buckets": list(counts.keys())
    }


@router.get("/kpis")
async def get_portfolio_kpis():
    """Get portfolio-level KPI metrics: total customers, avg risk, avg elasticity, active alerts."""
    return scoring_engine.get_portfolio_kpis()


@router.get("/behavioral-signals")
async def get_behavioral_signals():
    """
    Data Analytics Graph data — multi-source behavioral signals aggregated at portfolio level.
    Detects salary delays, savings decline, UPI lending spikes, failed auto-debits, etc.
    """
    signals = scoring_engine.get_portfolio_behavioral_signals()
    labels = list(signals.keys())
    display_labels = {
        "salary_delays": "Salary Delays",
        "savings_decline": "Savings Decline",
        "upi_lending_spikes": "UPI Lending Spikes",
        "failed_auto_debits": "Failed Auto-Debits",
        "high_atm_withdrawals": "High ATM Withdrawals",
        "utility_missed": "Utility Missed",
    }
    return {
        "labels": [display_labels.get(k, k) for k in labels],
        "values": [signals[k] for k in labels],
        "colors": ["#ef4444", "#f97316", "#8b5cf6", "#e11d48", "#0891b2", "#eab308"],
    }


@router.get("/predictive-forecast")
async def get_portfolio_predictive_forecast():
    """
    Predictive Analytics Graph data — portfolio-level default probability forecast for next 4 weeks.
    """
    return scoring_engine.get_portfolio_predictive_forecast()


@router.get("/region-delinquency")
async def get_region_delinquency():
    """
    Environment-Aware Analysis Graph data — top 5 regions by delinquent customer count.
    Uses model-predicted risk scores for delinquency classification.
    """
    data = scoring_engine.get_region_delinquency_data()
    # Limit to top 5 regions (already sorted DESC by delinquent_customers)
    top = data[:5]
    return {
        "regions": [d["region"] for d in top],
        "delinquent_customers": [d["delinquent_customers"] for d in top],
        "avg_risk_scores": [d["avg_risk_score"] for d in top],
        "total_customers": [d["total_customers"] for d in top],
        "raw": top,
    }

