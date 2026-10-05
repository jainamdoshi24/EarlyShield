"""
Summary Engine - Generate comprehensive daily and customer summaries
"""
from datetime import datetime
from backend.data.simulator import CustomerDataSimulator
from backend.engines.scoring_engine import calculate_risk_score, calculate_elasticity_score, get_automation_recommendations, get_risk_class_label
from backend.engines.alert_engine import get_customer_alerts

simulator = CustomerDataSimulator()


def get_todays_summary(customer_id: str = None) -> dict:
    """
    Get today's comprehensive summary for a specific customer or globally.
    """
    if customer_id:
        return _get_customer_summary(customer_id)
    else:
        return simulator.get_todays_alerts()


def _get_customer_summary(customer_id: str) -> dict:
    """Generate a full customer summary with all required fields."""
    customer_info = simulator.get_customer_info(customer_id)
    risk = calculate_risk_score(customer_id)
    elasticity = calculate_elasticity_score(customer_id)
    alerts = get_customer_alerts(customer_id)
    trend = customer_info.get('risk_trend', 'stable')
    base_risk = customer_info.get('base_risk', 0.5)

    # Risk movement
    if risk > base_risk + 0.05:
        risk_movement = "up"
    elif risk < base_risk - 0.05:
        risk_movement = "down"
    else:
        risk_movement = "stable"

    # Newly triggered signals
    signals = []
    if risk > 0.6:
        signals.append("High financial stress detected")
    if trend in ('increasing', 'critical'):
        signals.append("Risk trajectory trending upward")
    if elasticity < 0.8:
        signals.append("Low resilience — limited repayment capacity")

    failed_df = simulator.generate_auto_debit_failures(customer_id)
    failed_today = min(len(failed_df), 2) if not failed_df.empty else 0
    if failed_today > 0:
        signals.append(f"{failed_today} failed payment(s) in recent cycle")

    if customer_info.get('income_stability') in ('low', 'very_low'):
        signals.append("Income instability — salary credit irregularity noted")

    # Escalated alerts
    escalated = [a for a in alerts if a.get('severity') in ('critical', 'high')]

    # Recommendations
    recommendations = get_automation_recommendations(customer_id)

    # Quick insights
    class_label = get_risk_class_label(risk, trend)
    quick_insights = []
    if class_label == 'Critical':
        quick_insights.append("Customer is in critical risk zone — immediate banker intervention advised.")
    elif class_label == 'Escalating':
        quick_insights.append("Risk is escalating — proactive outreach can prevent default.")
    if elasticity > 1.5:
        quick_insights.append("Strong repayment elasticity — payment restructuring likely to succeed.")
    elif elasticity < 0.5:
        quick_insights.append("Very low elasticity — consider hardship program enrollment.")

    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "customer_id": customer_id,
        "customer_name": customer_info.get('name', 'Unknown'),
        "risk_score": round(risk * 100, 1),
        "risk_movement": risk_movement,
        "risk_class": class_label,
        "new_signals": signals,
        "escalated_alerts": len(escalated),
        "total_alerts": len(alerts),
        "failed_payments_today": failed_today,
        "recommendations": [r['description'] for r in recommendations],
        "automation_actions": recommendations,
        "quick_insights": quick_insights,
        "elasticity": round(elasticity, 2)
    }


def get_recommendations(customer_id: str) -> list:
    """Get tailored recommendations for a customer (backward compat)."""
    recs = get_automation_recommendations(customer_id)
    return [r['description'] for r in recs]
