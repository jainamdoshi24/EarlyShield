"""
Chatbot Engine - Advanced context-aware customer chatbot with conversation memory
"""
from backend.data.simulator import CustomerDataSimulator
from backend.engines.scoring_engine import (
    calculate_risk_score, calculate_elasticity_score,
    get_risk_class_label, get_predictive_forecast, get_automation_recommendations
)
from backend.engines.alert_engine import get_customer_alerts

simulator = CustomerDataSimulator()

# Conversation memory per customer
_conversation_memory = {}


def process_query(customer_id: str, query: str) -> dict:
    """
    Process a chatbot query with full customer context and conversation memory.
    Uses banking-tone language and comprehensive intent matching.
    """
    query_lower = query.lower().strip()

    # Init memory if needed
    if customer_id not in _conversation_memory:
        _conversation_memory[customer_id] = []

    # Record user query
    _conversation_memory[customer_id].append({"role": "user", "text": query})

    # Get customer context
    customer_info = simulator.get_customer_info(customer_id)
    name = customer_info.get('name', 'this customer')
    risk = calculate_risk_score(customer_id)
    elasticity = calculate_elasticity_score(customer_id)
    alerts = get_customer_alerts(customer_id)
    trend = customer_info.get('risk_trend', 'stable')
    class_label = get_risk_class_label(risk, trend)
    risk_pct = round(risk * 100, 1)

    response = _route_intent(query_lower, name, risk, risk_pct, elasticity, alerts, trend, class_label, customer_id, customer_info)

    # Record bot response
    _conversation_memory[customer_id].append({"role": "bot", "text": response["text"]})

    # Keep only last 20 messages
    if len(_conversation_memory[customer_id]) > 20:
        _conversation_memory[customer_id] = _conversation_memory[customer_id][-20:]

    return response


def _route_intent(query, name, risk, risk_pct, elasticity, alerts, trend, class_label, customer_id, info):
    """Route query to appropriate handler based on intent detection."""

    # Why high risk?
    if any(kw in query for kw in ['why', 'reason', 'cause', 'explain risk', 'high risk', 'what makes']):
        return _explain_risk(name, risk_pct, elasticity, trend, class_label, info)

    # What changed / last 7 days
    if any(kw in query for kw in ['changed', 'last 7', 'recent', 'this week', 'what happened', 'past week']):
        return _recent_changes(name, risk_pct, trend, class_label, alerts, info)

    # Signals / contributors
    if any(kw in query for kw in ['signal', 'contribut', 'factor', 'driver', 'indicator']):
        return _explain_signals(name, risk_pct, info, customer_id)

    # Elasticity
    if any(kw in query for kw in ['elasticity', 'resilience', 'capacity', 'ability']):
        return _explain_elasticity(name, elasticity, info)

    # Predictive / forecast
    if any(kw in query for kw in ['predict', 'forecast', 'future', 'next week', 'default probability', 'outlook']):
        return _explain_prediction(name, customer_id)

    # Intervention / recommendation / action
    if any(kw in query for kw in ['recommend', 'action', 'interven', 'what should', 'next step', 'suggest', 'help']):
        return _get_recommendations(name, customer_id, risk_pct)

    # Alert queries
    if any(kw in query for kw in ['alert', 'warning', 'issue', 'notification']):
        return _explain_alerts(name, alerts)

    # Risk score / general risk
    if any(kw in query for kw in ['risk', 'score', 'status', 'how is', 'overview']):
        return _explain_risk_score(name, risk_pct, class_label, trend, elasticity)

    # Greeting
    if any(kw in query for kw in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
        return {
            "text": f"Hello! I'm your EarlyShield AI assistant for {name}'s account. "
                    f"Current risk: {risk_pct}% ({class_label}). How can I help you today?",
            "type": "greeting"
        }

    # Default / fallback
    return {
        "text": f"I can assist you with {name}'s risk analysis. You can ask me:\n"
                f"• Why is this customer high risk?\n"
                f"• What signals are driving the score?\n"
                f"• What changed in the last 7 days?\n"
                f"• Explain the elasticity score\n"
                f"• What's the predictive forecast?\n"
                f"• What interventions do you recommend?",
        "type": "help"
    }


def _explain_risk(name, risk_pct, elasticity, trend, class_label, info):
    env = info.get('environment', 'N/A')
    income = info.get('income_stability', 'N/A')

    factors = []
    if risk_pct > 60:
        factors.append(f"elevated financial stress score of {risk_pct}%")
    if trend in ('increasing', 'critical'):
        factors.append(f"a {trend} risk trajectory")
    if elasticity < 1.0:
        factors.append(f"limited repayment elasticity ({elasticity:.2f}/2.0)")
    if income in ('low', 'very_low'):
        factors.append(f"{income.replace('_', ' ')} income stability")
    if env in ('rural', 'semi-urban'):
        factors.append(f"{env} geography with limited financial infrastructure")

    if not factors:
        factors.append("moderate risk indicators within acceptable thresholds")

    reason = ", ".join(factors)

    return {
        "text": f"**{name}** is classified as **{class_label}** (Risk: {risk_pct}%).\n\n"
                f"Key contributing factors: {reason}.\n\n"
                f"The current trend is **{trend}**, which {'warrants close monitoring' if trend in ('increasing', 'volatile', 'critical') else 'suggests stable conditions'}.",
        "type": "risk_explanation"
    }


def _recent_changes(name, risk_pct, trend, class_label, alerts, info):
    changes = []
    if trend in ('increasing', 'critical'):
        changes.append("Risk score has been trending upward over the past week")
    if len([a for a in alerts if a['severity'] in ('critical', 'high')]) > 0:
        changes.append(f"{len([a for a in alerts if a['severity'] in ('critical', 'high')])} high-priority alert(s) triggered")
    if info.get('income_stability') in ('low', 'very_low'):
        changes.append("Salary credit irregularity detected in recent cycle")
    if risk_pct > 50:
        changes.append("Auto-debit failure registered — potential cash flow issue")

    if not changes:
        changes.append("No significant changes detected in the last 7 days")

    change_list = "\n".join([f"• {c}" for c in changes])

    return {
        "text": f"**7-Day Change Analysis for {name}:**\n\n{change_list}\n\n"
                f"Current status: **{class_label}** ({risk_pct}%)",
        "type": "recent_changes"
    }


def _explain_signals(name, risk_pct, info, customer_id):
    signals = []
    base_risk = info.get('base_risk', 0.5)

    if base_risk > 0.6:
        signals.append("**Salary Credit Delay**: Payments received later than scheduled")
        signals.append("**Savings Decline**: Week-over-week balance reduction observed")
        signals.append("**ATM Withdrawal Spikes**: Possible cash-hoarding behavior")
    if base_risk > 0.4:
        signals.append("**UPI Lending App Transactions**: Increased activity with lending platforms")
        signals.append("**Reduced Discretionary Spending**: Spending on dining & entertainment has dropped")
    if base_risk > 0.3:
        signals.append("**Late Utility Payments**: Delay in utility bill settlements")

    if not signals:
        signals.append("No significant warning signals detected at this time")

    signal_list = "\n".join([f"• {s}" for s in signals])

    return {
        "text": f"**Key Signals for {name} (Risk: {risk_pct}%):**\n\n{signal_list}",
        "type": "signals"
    }


def _explain_elasticity(name, elasticity, info):
    income = info.get('income_stability', 'medium')
    env = info.get('environment', 'urban')

    level = "high" if elasticity > 1.2 else ("moderate" if elasticity > 0.7 else "low")

    return {
        "text": f"**Elasticity Score for {name}: {elasticity:.2f} / 2.0** ({level} resilience)\n\n"
                f"This score measures the customer's capacity to absorb financial stress without defaulting.\n\n"
                f"• **Income Stability**: {income.replace('_', ' ').title()}\n"
                f"• **Geography**: {env.title()} (affects access to financial services)\n"
                f"• **Interpretation**: {'This customer has strong repayment capacity and can withstand temporary stress.' if level == 'high' else ('Moderate capacity — may need support if stress persists beyond 2-3 months.' if level == 'moderate' else 'Limited capacity — high risk of default under continued stress. Proactive intervention recommended.')}",
        "type": "elasticity_info"
    }


def _explain_prediction(name, customer_id):
    forecast = get_predictive_forecast(customer_id)

    week_data = "\n".join([f"• **{w}**: {p}% default probability" for w, p in zip(forecast['weeks'], forecast['probabilities'])])

    return {
        "text": f"**Predictive Forecast for {name}:**\n\n"
                f"Classification: **{forecast['class_label']}**\n"
                f"Current Risk: {forecast['current_risk']}% | Trend: {forecast['trend'].title()}\n\n"
                f"{week_data}\n\n"
                f"{'⚠️ Immediate intervention recommended to prevent default escalation.' if forecast['class_label'] in ('Critical', 'Escalating') else 'Continue monitoring — current trajectory is manageable.'}",
        "type": "prediction"
    }


def _get_recommendations(name, customer_id, risk_pct):
    recs = get_automation_recommendations(customer_id)

    rec_list = "\n".join([f"• **{r['action']}** ({r['priority'].upper()}): {r['description']}" for r in recs])

    return {
        "text": f"**Recommended Interventions for {name} (Risk: {risk_pct}%):**\n\n{rec_list}",
        "type": "recommendations"
    }


def _explain_alerts(name, alerts):
    if not alerts:
        return {
            "text": f"No active alerts for **{name}**. The account is within normal parameters.",
            "type": "alerts"
        }

    alert_list = "\n".join([f"• **{a['severity'].upper()}**: {a['message']}" for a in alerts[:5]])

    return {
        "text": f"**Active Alerts for {name}** ({len(alerts)} total):\n\n{alert_list}",
        "type": "alerts"
    }


def _explain_risk_score(name, risk_pct, class_label, trend, elasticity):
    return {
        "text": f"**Risk Overview for {name}:**\n\n"
                f"• **Financial Stress Score**: {risk_pct}%\n"
                f"• **Risk Classification**: {class_label}\n"
                f"• **Trend**: {trend.title()}\n"
                f"• **Elasticity**: {elasticity:.2f}/2.0\n\n"
                f"{'This customer requires immediate attention.' if class_label in ('Critical', 'Escalating') else 'Current risk levels are manageable with standard monitoring.'}",
        "type": "risk_info"
    }


def get_conversation_history(customer_id: str) -> list:
    """Get conversation history for a customer."""
    return _conversation_memory.get(customer_id, [])


def clear_conversation(customer_id: str):
    """Clear conversation memory for a customer."""
    _conversation_memory.pop(customer_id, None)
