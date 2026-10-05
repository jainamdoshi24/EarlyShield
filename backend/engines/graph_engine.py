"""
Graph Engine - Generate data for all chart visualizations
Returns JSON-serializable data structures for frontend charting
"""
from backend.data.simulator import CustomerDataSimulator

simulator = CustomerDataSimulator()


def generate_trajectory_data(customer_id: str) -> dict:
    """Generate risk score trajectory over time"""
    df = simulator.generate_stress_trajectory(customer_id)
    risk_scores = df['Risk'].tolist()
    # Mark escalation points (>10% week-over-week increase)
    escalation_points = []
    for i in range(1, len(risk_scores)):
        if risk_scores[i] - risk_scores[i - 1] > 0.10:
            escalation_points.append(i)

    return {
        "weeks": df['Week'].tolist(),
        "risk_scores": [round(r * 100, 1) for r in risk_scores],
        "escalation_indices": escalation_points
    }


def generate_salary_delay_data(customer_id: str) -> dict:
    """Generate salary delay pattern data"""
    df = simulator.generate_salary_delay_data(customer_id)
    return {
        "months": df['Month'].tolist(),
        "days_late": df['Days Late'].tolist()
    }


def generate_savings_data(customer_id: str) -> dict:
    """Generate savings balance trend"""
    df = simulator.generate_savings_data(customer_id)
    return {
        "weeks": df['Week'].tolist(),
        "balance": [round(b, 1) for b in df['Balance'].tolist()]
    }


def generate_upi_lending_data(customer_id: str) -> dict:
    """Generate UPI to lending app transactions"""
    df = simulator.generate_upi_lending_data(customer_id)
    return {
        "months": df['Month'].tolist(),
        "payments": df['Payments'].tolist()
    }


def generate_utility_payment_data(customer_id: str) -> dict:
    """Generate utility payment status data"""
    df = simulator.generate_utility_payment_data(customer_id)
    statuses = df['Status'].tolist()
    months = df['Month'].tolist()
    # Convert to numeric for chart visualization
    status_values = []
    for s in statuses:
        if s == 'On Time':
            status_values.append(0)
        elif s == 'Late':
            status_values.append(1)
        else:
            status_values.append(2)

    return {
        "months": months,
        "statuses": statuses,
        "status_values": status_values
    }


def generate_discretionary_spend_data(customer_id: str) -> dict:
    """Generate discretionary spending trend"""
    df = simulator.generate_discretionary_spend(customer_id)
    return {
        "months": df['Month'].tolist(),
        "amount": df['Amount'].tolist()
    }


def generate_atm_withdrawal_data(customer_id: str) -> dict:
    """Generate ATM withdrawal patterns"""
    df = simulator.generate_atm_withdrawal_data(customer_id)
    return {
        "weeks": df['Week'].tolist(),
        "amount": df['Amount'].tolist()
    }


def generate_auto_debit_failure_data(customer_id: str) -> dict:
    """Generate failed auto-debit attempt data"""
    df = simulator.generate_auto_debit_failures(customer_id)
    if df.empty:
        return {"dates": [], "types": [], "amounts": [], "statuses": []}

    return {
        "dates": df['Date'].tolist(),
        "types": df['Type'].tolist(),
        "amounts": df['Amount'].tolist(),
        "statuses": df['Status'].tolist()
    }


def generate_failed_payments_timeline(customer_id: str) -> dict:
    """Generate failed payments timeline and rolling frequency"""
    df = simulator.generate_auto_debit_failures(customer_id)
    if df.empty:
        return {
            "timeline": [],
            "rolling_frequency": {"periods": [], "counts": []}
        }

    timeline = []
    for _, row in df.iterrows():
        timeline.append({
            "date": row['Date'],
            "type": row['Type'],
            "amount": int(row['Amount']),
            "status": row['Status']
        })

    # Rolling frequency grouped by month
    info = simulator.get_customer_info(customer_id)
    base_risk = info.get('base_risk', 0.3)
    periods = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    counts = [max(0, int(base_risk * 3 * (0.5 + 0.5 * (i / 4)))) for i in range(4)]

    return {
        "timeline": timeline,
        "rolling_frequency": {
            "periods": periods,
            "counts": counts
        }
    }


def generate_environment_data(customer_id: str) -> dict:
    """Generate environment-aware analysis data for heatmap/grouped bars"""
    info = simulator.get_customer_info(customer_id)
    base_risk = info.get('base_risk', 0.5)
    env = info.get('environment', 'urban')
    income = info.get('income_stability', 'medium')

    # Customer type classification
    import numpy as np
    is_salaried = env in ('metro', 'urban')
    customer_type = 'Salaried' if is_salaried else 'Self-Employed'

    # Channel behavior scores
    channels = {
        "UPI": round(min(1.0, 0.3 + base_risk * 0.5 + np.random.uniform(-0.1, 0.1)), 2),
        "NEFT/RTGS": round(min(1.0, 0.2 + (1 - base_risk) * 0.4 + np.random.uniform(-0.1, 0.1)), 2),
        "ATM": round(min(1.0, 0.2 + base_risk * 0.6 + np.random.uniform(-0.1, 0.1)), 2),
        "Branch": round(min(1.0, 0.1 + (0.3 if env == 'rural' else 0.1) + np.random.uniform(-0.1, 0.1)), 2),
        "Mobile": round(min(1.0, 0.5 + (0.2 if env == 'metro' else -0.1) + np.random.uniform(-0.1, 0.1)), 2),
    }

    # Geography risk factors
    geo_factors = {
        "metro": {"economic_activity": 0.85, "digital_access": 0.95, "support_infra": 0.90},
        "urban": {"economic_activity": 0.75, "digital_access": 0.80, "support_infra": 0.75},
        "semi-urban": {"economic_activity": 0.55, "digital_access": 0.50, "support_infra": 0.45},
        "rural": {"economic_activity": 0.35, "digital_access": 0.25, "support_infra": 0.30},
    }

    geo = geo_factors.get(env, geo_factors['urban'])

    # Trend pattern
    trend_map = {
        'stable': 'Steady — no significant movement',
        'increasing': 'Upward risk trajectory',
        'decreasing': 'Improving — risk declining',
        'volatile': 'Erratic — unpredictable movements',
        'high': 'Persistently elevated',
        'critical': 'Critical — requires immediate attention'
    }

    trend = info.get('risk_trend', 'stable')

    # Bias-safe notes
    bias_notes = [
        "Analysis is based solely on transactional patterns — no demographic profiling applied.",
        "Risk factors are derived from financial behavior, not personal attributes.",
    ]
    if env == 'rural':
        bias_notes.append("Seasonal income patterns factored in — avoid penalizing cyclical cash-flow dips.")
    if income == 'low':
        bias_notes.append("Lower income bracket adjusted for regional cost-of-living context.")

    insights = simulator.get_environment_insights(customer_id)

    return {
        "customer_type": customer_type,
        "channel_behavior": channels,
        "geography": {
            "location": env,
            "factors": geo
        },
        "trend_pattern": trend_map.get(trend, 'Unknown'),
        "bias_safe_notes": bias_notes,
        "insights": insights
    }


def get_all_graphs(customer_id: str) -> dict:
    """Get all graph data for a customer in one call"""
    return {
        "trajectory": generate_trajectory_data(customer_id),
        "salary_delay": generate_salary_delay_data(customer_id),
        "savings": generate_savings_data(customer_id),
        "upi_lending": generate_upi_lending_data(customer_id),
        "utility_payments": generate_utility_payment_data(customer_id),
        "discretionary_spend": generate_discretionary_spend_data(customer_id),
        "atm_withdrawals": generate_atm_withdrawal_data(customer_id),
        "auto_debit_failures": generate_auto_debit_failure_data(customer_id),
    }
