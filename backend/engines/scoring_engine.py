"""
Scoring Engine - Risk, elasticity, and predictive analytics using the ML model.

On module load, every customer is scored via model.predict_proba() and cached.
All segment counts, bucket assignments, and KPIs derive from these model scores.
"""
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from backend.engines.model_loader import model_loader
from backend.data.simulator import CustomerDataSimulator

simulator = CustomerDataSimulator()

# ── Risk score cache (populated on first access) ──────────────────────────────
_risk_cache: dict[str, float] = {}
_cache_ready = False

RISK_LABELS = {
    'stable': 'Stable',
    'emerging': 'Emerging',
    'escalating': 'Escalating',
    'critical': 'Critical'
}


def _build_risk_cache():
    """Score every customer with the loaded model and cache the results."""
    global _risk_cache, _cache_ready
    model = model_loader.model
    all_ids = simulator.get_customer_list()
    new_cache: dict[str, float] = {}

    for cid in all_ids:
        customer_info = simulator.get_customer_info(cid)
        if not customer_info:
            new_cache[cid] = 0.5
            continue
        if model is not None:
            try:
                features = simulator.generate_features(cid)
                score = float(model.predict_proba([features])[0][1])
            except Exception:
                score = customer_info.get('base_risk', 0.5)
        else:
            score = customer_info.get('base_risk', 0.5)
        new_cache[cid] = max(0.0, min(1.0, score))

    _risk_cache = new_cache
    _cache_ready = True
    print(f"✓ Risk cache built for {len(_risk_cache)} customers using "
          f"{'ML model' if model is not None else 'base_risk fallback'}")

    # Log distribution summary
    buckets = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80%+": 0}
    for score in _risk_cache.values():
        buckets[get_risk_bucket(score)] += 1
    print(f"  Segment distribution: {buckets}")


def rebuild_risk_cache():
    """Public API to force-rebuild the cache (e.g. after model reload)."""
    _build_risk_cache()


def _ensure_cache():
    """Lazily build the cache on first use."""
    if not _cache_ready:
        _build_risk_cache()


# ── Per-customer scoring ──────────────────────────────────────────────────────

def calculate_risk_score(customer_id: str) -> float:
    """Return cached model-predicted risk score for a customer (0–1)."""
    _ensure_cache()
    if customer_id in _risk_cache:
        return _risk_cache[customer_id]
    # Customer not in cache (shouldn't happen normally) — compute live
    try:
        customer_info = simulator.get_customer_info(customer_id)
        if not customer_info:
            return 0.5
        model = model_loader.model
        if model:
            features = simulator.generate_features(customer_id)
            try:
                risk_score = float(model.predict_proba([features])[0][1])
            except Exception:
                risk_score = customer_info.get('base_risk', 0.5)
        else:
            risk_score = customer_info.get('base_risk', 0.5)
        score = max(0.0, min(1.0, risk_score))
        _risk_cache[customer_id] = score  # cache it
        return score
    except Exception as e:
        print(f"Error calculating risk score for {customer_id}: {e}")
        return simulator.get_customer_info(customer_id).get('base_risk', 0.5)


def calculate_elasticity_score(customer_id: str) -> float:
    return simulator.calculate_elasticity_score(customer_id)


# ── Bucket / segment helpers (all use model scores) ──────────────────────────

def get_risk_bucket(risk_score: float) -> str:
    """Assign a risk bucket based on the model-predicted risk score (0–1)."""
    if risk_score < 0.20:
        return "0-20%"
    elif risk_score < 0.40:
        return "20-40%"
    elif risk_score < 0.60:
        return "40-60%"
    elif risk_score < 0.80:
        return "60-80%"
    return "80%+"


def get_risk_segment_counts() -> dict:
    """Count customers per segment using MODEL-PREDICTED scores."""
    _ensure_cache()
    counts = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80%+": 0}
    for score in _risk_cache.values():
        counts[get_risk_bucket(score)] += 1
    return counts


def get_customers_by_bucket(bucket: str) -> list:
    """Return customer IDs whose MODEL-PREDICTED score falls in the given bucket."""
    _ensure_cache()
    return [cid for cid, score in _risk_cache.items()
            if get_risk_bucket(score) == bucket]


def get_risk_class_label(risk_score: float, trend: str) -> str:
    if risk_score >= 0.80:
        return 'Critical'
    elif risk_score >= 0.60:
        return 'Escalating'
    elif risk_score >= 0.40 or trend in ('increasing', 'volatile'):
        return 'Emerging'
    return 'Stable'


# ── Predictive forecast ───────────────────────────────────────────────────────

def get_predictive_forecast(customer_id: str) -> dict:
    """Generate default probability forecast for next 4 weeks using the model."""
    customer_info = simulator.get_customer_info(customer_id)
    risk = calculate_risk_score(customer_id)
    trend = customer_info.get('risk_trend', 'stable')
    elasticity = calculate_elasticity_score(customer_id)

    weeks = [1, 2, 3, 4]
    trend_factor = {
        'stable': 0.0,
        'decreasing': -0.025,
        'increasing': 0.035,
        'volatile': 0.02,
        'high': 0.015,
        'critical': 0.045
    }.get(trend, 0.0)

    rng = np.random.default_rng(sum(ord(c) for c in customer_id))
    forecasts = []
    for w in weeks:
        damping = max(0.3, elasticity / 2.0)
        projected = risk + (trend_factor * w * (1 - damping * 0.3))
        noise = rng.uniform(-0.01, 0.01)
        projected = max(0.0, min(1.0, projected + noise))
        forecasts.append(round(projected * 100, 1))

    return {
        "weeks": [f"Week {w}" for w in weeks],
        "probabilities": forecasts,
        "current_risk": round(risk * 100, 1),
        "class_label": get_risk_class_label(risk, trend),
        "trend": trend,
        "elasticity": round(elasticity, 2)
    }


# ── Automation recommendations ────────────────────────────────────────────────

def get_automation_recommendations(customer_id: str) -> list:
    """Auto-route recommended interventions based on risk and signals."""
    risk = calculate_risk_score(customer_id)
    elasticity = calculate_elasticity_score(customer_id)
    customer_info = simulator.get_customer_info(customer_id)
    trend = customer_info.get('risk_trend', 'stable')

    recommendations = []

    if risk >= 0.8:
        recommendations += [
            {"action": "Credit Consolidation Support", "priority": "critical",
             "description": "Immediate credit consolidation review — risk score exceeds 80%"},
            {"action": "Payment Holiday", "priority": "critical",
             "description": "Offer 30-day payment holiday to prevent default"},
        ]
    elif risk >= 0.6:
        recommendations += [
            {"action": "EMI Date Shift", "priority": "high",
             "description": "Shift EMI date to align with salary credit cycle"},
            {"action": "Payment Holiday", "priority": "high",
             "description": "Consider short-term payment holiday if stress persists"},
        ]
    elif risk >= 0.4:
        recommendations.append({"action": "EMI Date Shift", "priority": "medium",
                                 "description": "Proactive EMI date alignment recommended"})

    if trend in ('increasing', 'critical', 'volatile'):
        recommendations.append({"action": "Proactive Outreach", "priority": "high",
                                 "description": "Customer shows worsening trend — initiate banker outreach"})

    if elasticity < 0.5:
        recommendations.append({"action": "Credit Consolidation Support", "priority": "high",
                                 "description": "Low elasticity indicates fragile financial state"})

    if not recommendations:
        recommendations.append({"action": "Standard Monitoring", "priority": "low",
                                 "description": "Continue regular monitoring — no immediate action required"})

    return recommendations


# ── Portfolio-level analytics (use model scores) ──────────────────────────────

def get_portfolio_kpis() -> dict:
    """Portfolio KPIs using model-predicted risk scores."""
    _ensure_cache()
    total = len(_risk_cache)
    risks = list(_risk_cache.values())
    elasticities = [calculate_elasticity_score(cid) for cid in _risk_cache]
    avg_risk = round(float(np.mean(risks)) * 100, 1) if risks else 0.0
    avg_elasticity = round(float(np.mean(elasticities)), 2) if elasticities else 0.0
    active_alerts = sum(1 for r in risks if r > 0.6)
    return {
        "total_customers": total,
        "avg_risk_score": avg_risk,
        "avg_elasticity_score": avg_elasticity,
        "active_alerts_today": active_alerts,
    }


def get_portfolio_behavioral_signals() -> dict:
    """Aggregate behavioral signals using model-predicted scores."""
    _ensure_cache()
    signals = {
        "salary_delays": 0,
        "savings_decline": 0,
        "upi_lending_spikes": 0,
        "failed_auto_debits": 0,
        "high_atm_withdrawals": 0,
        "utility_missed": 0,
    }
    for cid, score in _risk_cache.items():
        signals["salary_delays"] += 1 if score > 0.4 else 0
        signals["savings_decline"] += 1 if score > 0.5 else 0
        signals["upi_lending_spikes"] += 1 if score > 0.55 else 0
        signals["failed_auto_debits"] += 1 if score > 0.45 else 0
        signals["high_atm_withdrawals"] += 1 if score > 0.65 else 0
        signals["utility_missed"] += 1 if score > 0.6 else 0
    return signals


def get_portfolio_predictive_forecast() -> dict:
    """Portfolio-level default probability forecast using model scores."""
    _ensure_cache()
    risks = list(_risk_cache.values())
    avg = float(np.mean(risks)) if risks else 0.0
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    probs = [round((avg + 0.01 * i) * 100, 1) for i in range(4)]
    high_risk_count = sum(1 for r in risks if r > 0.6)
    critical_count = sum(1 for r in risks if r > 0.8)
    return {
        "weeks": weeks,
        "avg_default_probability": probs,
        "high_risk_count": high_risk_count,
        "critical_count": critical_count,
        "total": len(risks),
    }


def get_region_delinquency_data() -> list:
    """Region-wise delinquency using model-predicted scores."""
    _ensure_cache()
    region_data = {}
    for cid, score in _risk_cache.items():
        info = simulator.get_customer_info(cid)
        region = info.get("region", "Unknown")
        if region not in region_data:
            region_data[region] = {"count": 0, "delinquent": 0, "risk_sum": 0.0}
        region_data[region]["count"] += 1
        region_data[region]["risk_sum"] += score
        if score > 0.4:
            region_data[region]["delinquent"] += 1

    result = []
    for region, d in region_data.items():
        result.append({
            "region": region,
            "total_customers": d["count"],
            "delinquent_customers": d["delinquent"],
            "avg_risk_score": round(d["risk_sum"] / d["count"] * 100, 1),
        })
    result.sort(key=lambda x: (x["delinquent_customers"], x["avg_risk_score"]), reverse=True)
    return result
