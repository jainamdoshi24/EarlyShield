"""
Alert Engine - Smart alerting mechanism with severity, prioritization, and escalation
"""
from datetime import datetime
from backend.data.simulator import CustomerDataSimulator
from backend.engines.scoring_engine import calculate_risk_score

simulator = CustomerDataSimulator()

# In-memory alert tracking for noise suppression
_alert_history = {}


def get_customer_alerts(customer_id: str) -> list:
    """
    Get all active alerts for a specific customer with smart prioritization.
    Includes escalation logic and noise suppression.
    """
    alerts = []
    customer_info = simulator.get_customer_info(customer_id)
    risk = calculate_risk_score(customer_id)
    trend = customer_info.get('risk_trend', 'stable')
    base_risk = customer_info.get('base_risk', 0.5)

    # --- Critical Escalation: Risk jump > 15% ---
    historical_risk = base_risk * 0.85  # simulated previous
    risk_jump = risk - historical_risk
    if risk_jump > 0.15:
        alerts.append({
            "type": "risk_jump",
            "severity": "critical",
            "message": f"Risk score jumped {risk_jump:.0%} — immediate review required",
            "icon": "alert-triangle",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # --- Critical: ≥2 failed payments in 3 days ---
    failed_df = simulator.generate_auto_debit_failures(customer_id)
    if not failed_df.empty:
        recent_failures = len(failed_df.head(3))
        if recent_failures >= 2:
            alerts.append({
                "type": "failed_payments_cluster",
                "severity": "critical",
                "message": f"{recent_failures} failed payments detected in recent period — escalated",
                "icon": "credit-card",
                "timestamp": datetime.now().strftime('%H:%M')
            })

    # --- High Risk Alert ---
    if risk > 0.6:
        severity = "critical" if risk > 0.8 else "high"
        alerts.append({
            "type": "high_risk",
            "severity": severity,
            "message": f"Risk score elevated to {risk:.1%} — {severity.upper()} priority",
            "icon": "shield-alert",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # --- Rising Trend Alert ---
    if trend in ('increasing', 'critical'):
        alerts.append({
            "type": "rising_risk",
            "severity": "high" if trend == 'critical' else "medium",
            "message": f"Risk trajectory: {trend.capitalize()} — monitor closely",
            "icon": "trending-up",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # --- Auto-debit failure alert ---
    if risk > 0.5 and not failed_df.empty:
        alerts.append({
            "type": "auto_debit_failed",
            "severity": "high",
            "message": "Recent auto-debit payment failed — insufficient funds",
            "icon": "credit-card",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # --- Savings decline alert ---
    if risk > 0.4:
        alerts.append({
            "type": "savings_decline",
            "severity": "medium",
            "message": "Savings account balance declining week-over-week",
            "icon": "piggy-bank",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # --- Low severity monitoring ---
    if 0.2 < risk <= 0.4:
        alerts.append({
            "type": "monitoring",
            "severity": "low",
            "message": "Standard monitoring active — no immediate risk",
            "icon": "eye",
            "timestamp": datetime.now().strftime('%H:%M')
        })

    # Noise suppression: remove duplicate minor alerts
    alerts = _suppress_noise(customer_id, alerts)

    return prioritize_alerts(alerts)


def _suppress_noise(customer_id: str, alerts: list) -> list:
    """
    Suppress repetitive minor events.
    Only suppress 'low' and some 'medium' alerts that repeat.
    """
    key = customer_id
    prev = _alert_history.get(key, set())
    filtered = []
    current_types = set()

    for alert in alerts:
        alert_key = f"{alert['type']}_{alert['severity']}"
        # Never suppress critical or high
        if alert['severity'] in ('critical', 'high'):
            filtered.append(alert)
            current_types.add(alert_key)
        elif alert_key not in prev:
            # New alert, keep it
            filtered.append(alert)
            current_types.add(alert_key)
        # Else skip (suppressed)

    _alert_history[key] = current_types
    return filtered


def get_global_alerts() -> dict:
    """Get today's alerts across all customers"""
    return simulator.get_todays_alerts()


def prioritize_alerts(alerts: list) -> list:
    """Sort alerts by severity (critical first)"""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(alerts, key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
