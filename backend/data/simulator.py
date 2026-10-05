"""
Data Simulator for EarlyShield AI Dashboard
Generates realistic demo data for all 37 model features across 50 customers.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Seed for reproducibility ──────────────────────────────────────────────────
RNG = np.random.default_rng(42)

# ── Customer master data (50 customers across all risk tiers) ─────────────────
_CUSTOMERS_RAW = [
    # id, name, region, env, income_stability, base_risk, trend
    ("CUST100","Rajesh Kumar","Mumbai","metro","high",0.10,"stable"),
    ("CUST101","Sneha Reddy","Hyderabad","metro","high",0.08,"stable"),
    ("CUST102","Arjun Menon","Bangalore","urban","high",0.14,"decreasing"),
    ("CUST103","Kavita Iyer","Chennai","metro","medium",0.17,"stable"),
    ("CUST104","Suresh Nair","Pune","urban","high",0.11,"stable"),
    ("CUST105","Divya Pillai","Kochi","urban","high",0.09,"stable"),
    ("CUST106","Nikhil Jain","Delhi","metro","high",0.13,"stable"),
    ("CUST107","Ananya Bose","Kolkata","urban","medium",0.16,"stable"),
    ("CUST108","Ritu Sharma","Jaipur","urban","high",0.12,"decreasing"),
    ("CUST109","Tarun Mehta","Ahmedabad","urban","high",0.15,"stable"),

    ("CUST200","Priya Sharma","Nagpur","semi-urban","medium",0.25,"stable"),
    ("CUST201","Rahul Gupta","Lucknow","urban","medium",0.32,"increasing"),
    ("CUST202","Deepa Rao","Coimbatore","semi-urban","medium",0.28,"stable"),
    ("CUST203","Manish Joshi","Bhopal","semi-urban","low",0.35,"volatile"),
    ("CUST204","Anita Desai","Surat","urban","medium",0.22,"stable"),
    ("CUST205","Kiran Bhat","Mysore","semi-urban","medium",0.38,"increasing"),
    ("CUST206","Shalini Verma","Indore","semi-urban","medium",0.30,"stable"),
    ("CUST207","Aakash Patel","Vadodara","urban","medium",0.27,"increasing"),
    ("CUST208","Rekha Nair","Thrissur","semi-urban","low",0.34,"volatile"),
    ("CUST209","Vinod Kumar","Agra","semi-urban","medium",0.36,"stable"),

    ("CUST300","Amit Patel","Nashik","semi-urban","low",0.45,"increasing"),
    ("CUST301","Lakshmi Krishnan","Madurai","rural","low",0.52,"volatile"),
    ("CUST302","Ravi Verma","Kanpur","urban","low",0.48,"increasing"),
    ("CUST303","Meera Kapoor","Jodhpur","semi-urban","medium",0.42,"stable"),
    ("CUST304","Sanjay Pillai","Trivandrum","rural","low",0.55,"increasing"),
    ("CUST305","Pooja Agarwal","Allahabad","urban","low",0.58,"volatile"),
    ("CUST306","Ramesh Yadav","Varanasi","rural","low",0.50,"increasing"),
    ("CUST307","Sunita Devi","Patna","rural","low",0.53,"volatile"),
    ("CUST308","Girish Menon","Mangalore","semi-urban","medium",0.44,"stable"),
    ("CUST309","Bhavna Shah","Rajkot","semi-urban","low",0.57,"increasing"),

    ("CUST400","Vikram Singh","Ranchi","rural","low",0.65,"high"),
    ("CUST401","Nandini Shah","Aurangabad","semi-urban","low",0.72,"increasing"),
    ("CUST402","Anil Yadav","Guwahati","rural","low",0.68,"volatile"),
    ("CUST403","Swati Malhotra","Amritsar","urban","low",0.62,"increasing"),
    ("CUST404","Harish Kulkarni","Hubli","rural","very_low",0.78,"high"),
    ("CUST405","Prem Chand","Meerut","semi-urban","low",0.63,"increasing"),
    ("CUST406","Savita Rani","Gwalior","rural","low",0.70,"high"),
    ("CUST407","Deepak Tomar","Jabalpur","rural","very_low",0.75,"volatile"),
    ("CUST408","Kaveri Nair","Kozhikode","semi-urban","low",0.66,"increasing"),
    ("CUST409","Sunil Pandey","Gorakhpur","rural","low",0.73,"high"),

    ("CUST500","Dinesh Tiwari","Dhanbad","rural","very_low",0.85,"critical"),
    ("CUST501","Geeta Pandey","Bareilly","semi-urban","very_low",0.92,"critical"),
    ("CUST502","Mohan Das","Muzaffarpur","rural","very_low",0.88,"critical"),
    ("CUST503","Lata Kumari","Bhagalpur","rural","very_low",0.82,"critical"),
    ("CUST504","Santosh Gupta","Saharanpur","semi-urban","very_low",0.90,"critical"),
    ("CUST505","Kamla Devi","Firozabad","rural","very_low",0.87,"critical"),
    ("CUST506","Ratan Lal","Aligarh","rural","very_low",0.83,"critical"),
    ("CUST507","Pushpa Rani","Moradabad","semi-urban","very_low",0.91,"critical"),
    ("CUST508","Jagdish Prasad","Jhansi","rural","very_low",0.86,"critical"),
    ("CUST509","Urmila Devi","Rampur","rural","very_low",0.89,"critical"),
]

# Build customer dict
_CUSTOMERS = {}
for row in _CUSTOMERS_RAW:
    cid, name, region, env, income_stability, base_risk, trend = row
    _CUSTOMERS[cid] = {
        "name": name,
        "region": region,
        "environment": env,
        "income_stability": income_stability,
        "base_risk": base_risk,
        "risk_trend": trend,
    }

# ── Feature generation helpers ────────────────────────────────────────────────
def _seed_for(customer_id: str) -> int:
    return sum(ord(c) for c in customer_id)


def _generate_model_features(customer_id: str) -> dict:
    """
    Generate all 37 model features for a customer.
    Features are derived deterministically from base_risk and customer profile.
    """
    info = _CUSTOMERS.get(customer_id, {})
    base_risk = info.get("base_risk", 0.5)
    env = info.get("environment", "urban")
    income_stab = info.get("income_stability", "medium")
    rng = np.random.default_rng(_seed_for(customer_id))

    # Income: higher risk → lower income
    income = rng.uniform(20000, 80000) * (1 - base_risk * 0.6)

    name_email_similarity = rng.uniform(0.3, 1.0) * (1 - base_risk * 0.3)
    prev_address_months = int(rng.uniform(0, 60) * (1 - base_risk * 0.5))
    current_address_months = int(rng.uniform(1, 48) * (1 - base_risk * 0.4))
    customer_age = int(rng.uniform(22, 65))
    days_since_request = int(rng.uniform(0, 30) * (1 + base_risk))
    intended_balcon_amount = rng.uniform(0, 5000) * base_risk
    zip_count_4w = int(rng.uniform(1, 10) * (1 + base_risk * 2))
    velocity_6h = rng.uniform(0, 10) * (1 + base_risk * 3)
    velocity_24h = rng.uniform(0, 20) * (1 + base_risk * 2)
    velocity_4w = rng.uniform(0, 50) * (1 + base_risk)
    bank_branch_count_8w = int(rng.uniform(0, 5) * (1 + base_risk))
    date_of_birth_distinct_emails_4w = int(rng.uniform(0, 3) * base_risk)
    credit_risk_score = int(rng.uniform(300, 850) * (1 - base_risk * 0.5))
    email_is_free = int(base_risk > 0.4)
    phone_home_valid = int(rng.uniform(0, 1) > base_risk * 0.5)
    phone_mobile_valid = int(rng.uniform(0, 1) > base_risk * 0.3)
    bank_months_count = int(rng.uniform(1, 120) * (1 - base_risk * 0.4))
    has_other_cards = int(base_risk > 0.3)
    proposed_credit_limit = rng.uniform(1000, 20000) * (1 - base_risk * 0.5)
    foreign_request = int(base_risk > 0.7 and rng.random() > 0.7)
    session_length_in_minutes = rng.uniform(1, 30) * (1 + base_risk)
    device_distinct_emails_8w = int(rng.uniform(0, 5) * base_risk)
    device_fraud_count = int(rng.uniform(0, 3) * base_risk)
    payment_type_enc = int(rng.choice([0, 1, 2, 3, 4]))
    employment_status_enc = int(rng.choice([0, 1, 2, 3]))
    housing_status_enc = int(rng.choice([0, 1, 2]))
    source_enc = int(rng.choice([0, 1, 2]))
    device_os_enc = int(rng.choice([0, 1, 2, 3]))
    velocity_ratio_6h_24h = velocity_6h / max(velocity_24h, 0.01)
    address_stability = (prev_address_months + current_address_months) / 120.0
    digital_footprint_risk = (device_distinct_emails_8w + device_fraud_count) / 8.0
    credit_exposure_ratio = intended_balcon_amount / max(income, 1)
    age_risk_flag = int(customer_age < 25 or customer_age > 60)
    high_velocity_flag = int(velocity_6h > 5)
    multi_device_flag = int(device_distinct_emails_8w > 2)
    cvi = base_risk * 100 + rng.uniform(-5, 5)

    return {
        "income": round(income, 2),
        "name_email_similarity": round(name_email_similarity, 4),
        "prev_address_months_count": prev_address_months,
        "current_address_months_count": current_address_months,
        "customer_age": customer_age,
        "days_since_request": days_since_request,
        "intended_balcon_amount": round(intended_balcon_amount, 2),
        "zip_count_4w": zip_count_4w,
        "velocity_6h": round(velocity_6h, 4),
        "velocity_24h": round(velocity_24h, 4),
        "velocity_4w": round(velocity_4w, 4),
        "bank_branch_count_8w": bank_branch_count_8w,
        "date_of_birth_distinct_emails_4w": date_of_birth_distinct_emails_4w,
        "credit_risk_score": credit_risk_score,
        "email_is_free": email_is_free,
        "phone_home_valid": phone_home_valid,
        "phone_mobile_valid": phone_mobile_valid,
        "bank_months_count": bank_months_count,
        "has_other_cards": has_other_cards,
        "proposed_credit_limit": round(proposed_credit_limit, 2),
        "foreign_request": foreign_request,
        "session_length_in_minutes": round(session_length_in_minutes, 2),
        "device_distinct_emails_8w": device_distinct_emails_8w,
        "device_fraud_count": device_fraud_count,
        "payment_type_enc": payment_type_enc,
        "employment_status_enc": employment_status_enc,
        "housing_status_enc": housing_status_enc,
        "source_enc": source_enc,
        "device_os_enc": device_os_enc,
        "velocity_ratio_6h_24h": round(velocity_ratio_6h_24h, 4),
        "address_stability": round(address_stability, 4),
        "digital_footprint_risk": round(digital_footprint_risk, 4),
        "credit_exposure_ratio": round(credit_exposure_ratio, 6),
        "age_risk_flag": age_risk_flag,
        "high_velocity_flag": high_velocity_flag,
        "multi_device_flag": multi_device_flag,
        "CVI": round(cvi, 2),
    }


# ── Main Simulator class ──────────────────────────────────────────────────────
class CustomerDataSimulator:
    """Simulates customer data for EarlyShield AI Dashboard"""

    def __init__(self):
        self.customers = _CUSTOMERS

    # ── Basic helpers ─────────────────────────────────────────────────────────
    def get_customer_list(self):
        return list(self.customers.keys())

    def get_customer_info(self, customer_id):
        return self.customers.get(customer_id, {})

    def get_risk_bucket(self, risk_score):
        if risk_score < 0.20:
            return "0-20%"
        elif risk_score < 0.40:
            return "20-40%"
        elif risk_score < 0.60:
            return "40-60%"
        elif risk_score < 0.80:
            return "60-80%"
        return "80%+"

    def get_customers_by_bucket(self, bucket):
        return [cid for cid, info in self.customers.items()
                if self.get_risk_bucket(info["base_risk"]) == bucket]

    def get_risk_segment_counts(self):
        counts = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80%+": 0}
        for info in self.customers.values():
            counts[self.get_risk_bucket(info["base_risk"])] += 1
        return counts

    # ── Feature generation ────────────────────────────────────────────────────
    def generate_features(self, customer_id):
        """Return feature vector in model's expected order."""
        feat = _generate_model_features(customer_id)
        MODEL_FEATURE_ORDER = [
            "income", "name_email_similarity", "prev_address_months_count",
            "current_address_months_count", "customer_age", "days_since_request",
            "intended_balcon_amount", "zip_count_4w", "velocity_6h", "velocity_24h",
            "velocity_4w", "bank_branch_count_8w", "date_of_birth_distinct_emails_4w",
            "credit_risk_score", "email_is_free", "phone_home_valid",
            "phone_mobile_valid", "bank_months_count", "has_other_cards",
            "proposed_credit_limit", "foreign_request", "session_length_in_minutes",
            "device_distinct_emails_8w", "device_fraud_count", "payment_type_enc",
            "employment_status_enc", "housing_status_enc", "source_enc",
            "device_os_enc", "velocity_ratio_6h_24h", "address_stability",
            "digital_footprint_risk", "credit_exposure_ratio", "age_risk_flag",
            "high_velocity_flag", "multi_device_flag", "CVI",
        ]
        return [feat.get(f, 0.0) for f in MODEL_FEATURE_ORDER]

    def get_all_features(self, customer_id):
        return _generate_model_features(customer_id)

    # ── Elasticity ────────────────────────────────────────────────────────────
    def calculate_elasticity_score(self, customer_id):
        info = self.customers.get(customer_id)
        if not info:
            return 1.0
        base_risk = info["base_risk"]
        elasticity = 2.0 - (base_risk * 2.0)
        stability_mod = {"very_low": -0.3, "low": -0.15, "medium": 0.0, "high": 0.2}
        env_mod = {"rural": -0.1, "semi-urban": -0.05, "urban": 0.05, "metro": 0.1}
        elasticity += stability_mod.get(info.get("income_stability", "medium"), 0.0)
        elasticity += env_mod.get(info.get("environment", "urban"), 0.0)
        return round(max(0.0, min(2.0, elasticity)), 2)

    # ── Time-series graphs ────────────────────────────────────────────────────
    def generate_stress_trajectory(self, customer_id, weeks=12):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.5)
        trend = info.get("risk_trend", "stable")
        rng = np.random.default_rng(_seed_for(customer_id) + 1)
        weeks_ago = list(range(weeks, 0, -1))
        risk_values = []
        for i, _ in enumerate(weeks_ago):
            if trend == "stable":
                r = base_risk + rng.uniform(-0.05, 0.05)
            elif trend == "increasing":
                r = base_risk * (0.65 + 0.35 * (i / weeks)) + rng.uniform(-0.03, 0.03)
            elif trend == "decreasing":
                r = base_risk * (1.2 - 0.2 * (i / weeks)) + rng.uniform(-0.03, 0.03)
            elif trend == "volatile":
                r = base_risk + rng.uniform(-0.18, 0.18)
            elif trend in ("high", "critical"):
                r = base_risk + rng.uniform(-0.08, 0.08)
            else:
                r = base_risk
            risk_values.append(float(np.clip(r, 0, 1)))
        return pd.DataFrame({"Week": [f"{w}w ago" for w in weeks_ago], "Risk": risk_values})

    def generate_salary_delay_data(self, customer_id, months=6):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        rng = np.random.default_rng(_seed_for(customer_id) + 2)
        current_date = datetime.now()
        month_names = [(current_date - timedelta(days=30 * i)).strftime("%b") for i in range(months - 1, -1, -1)]
        delays = []
        for _ in range(months):
            if base_risk < 0.3:
                d = 0 if rng.random() > 0.2 else int(rng.integers(1, 3))
            elif base_risk < 0.6:
                d = int(rng.integers(0, 6))
            else:
                d = int(rng.integers(3, 16))
            delays.append(d)
        return pd.DataFrame({"Month": month_names, "Days Late": delays})

    def generate_savings_data(self, customer_id, weeks=12):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.5)
        rng = np.random.default_rng(_seed_for(customer_id) + 3)
        start_balance = 100 * (1 - base_risk) * rng.uniform(0.8, 1.2)
        weeks_ago = list(range(weeks, 0, -1))
        balances = []
        for i in range(weeks):
            if base_risk > 0.6:
                b = start_balance * (1 - 0.08 * (i / weeks))
            else:
                b = start_balance * (1 + 0.04 * (i / weeks))
            balances.append(float(max(0, b + rng.uniform(-5, 5))))
        return pd.DataFrame({"Week": [f"{w}w ago" for w in weeks_ago], "Balance": balances})

    def generate_upi_lending_data(self, customer_id, months=6):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        trend = info.get("risk_trend", "stable")
        rng = np.random.default_rng(_seed_for(customer_id) + 4)
        current_date = datetime.now()
        month_names = [(current_date - timedelta(days=30 * i)).strftime("%b") for i in range(months - 1, -1, -1)]
        counts = []
        for i in range(months):
            if base_risk < 0.2:
                c = 0
            elif base_risk < 0.5:
                c = int(rng.integers(0, 3))
            else:
                base_c = int(base_risk * 5)
                t = i / months if trend in ("increasing", "critical") else 0.5
                c = int(base_c * (0.5 + t)) + int(rng.integers(0, 3))
            counts.append(c)
        return pd.DataFrame({"Month": month_names, "Payments": counts})

    def generate_utility_payment_data(self, customer_id, months=6):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        rng = np.random.default_rng(_seed_for(customer_id) + 5)
        current_date = datetime.now()
        month_names = [(current_date - timedelta(days=30 * i)).strftime("%b") for i in range(months - 1, -1, -1)]
        statuses = []
        for _ in range(months):
            rand = rng.random()
            if base_risk < 0.3:
                s = "On Time" if rand > 0.05 else "Late"
            elif base_risk < 0.6:
                s = "On Time" if rand > 0.3 else ("Late" if rand > 0.1 else "Missed")
            else:
                s = "Missed" if rand > 0.4 else ("Late" if rand > 0.2 else "On Time")
            statuses.append(s)
        return pd.DataFrame({"Month": month_names, "Status": statuses})

    def generate_discretionary_spend(self, customer_id, months=6):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        rng = np.random.default_rng(_seed_for(customer_id) + 6)
        current_date = datetime.now()
        month_names = [(current_date - timedelta(days=30 * i)).strftime("%b") for i in range(months - 1, -1, -1)]
        base_spend = 15000 * (1 - base_risk * 0.5)
        amounts = []
        for i in range(months):
            tf = (1.0 - 0.5 * (i / months)) if base_risk > 0.6 else (1.0 + 0.1 * (i / months))
            amounts.append(int(base_spend * tf * rng.uniform(0.9, 1.1)))
        return pd.DataFrame({"Month": month_names, "Amount": amounts})

    def generate_atm_withdrawal_data(self, customer_id, weeks=8):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        rng = np.random.default_rng(_seed_for(customer_id) + 7)
        weeks_ago = list(range(weeks, 0, -1))
        amounts = []
        for _ in range(weeks):
            if base_risk > 0.7:
                mult = 3.0 if rng.random() < 0.4 else 0.5
            else:
                mult = 1.0
            amounts.append(int(2000 * mult * rng.uniform(0.8, 1.2)))
        return pd.DataFrame({"Week": [f"{w}w ago" for w in weeks_ago], "Amount": amounts})

    def generate_auto_debit_failures(self, customer_id, months=6):
        info = self.customers.get(customer_id, {})
        base_risk = info.get("base_risk", 0.3)
        rng = np.random.default_rng(_seed_for(customer_id) + 8)
        data = []
        current_date = datetime.now()
        failure_prob = base_risk * 0.8
        for i in range(months):
            month_date = current_date - timedelta(days=30 * i)
            for tx_type, amount in [("Loan EMI", 12000), ("SIP", 5000), ("Credit Card", 8000)]:
                if rng.random() < failure_prob:
                    data.append({
                        "Date": (month_date + timedelta(days=int(rng.integers(1, 28)))).strftime("%Y-%m-%d"),
                        "Type": tx_type,
                        "Amount": amount,
                        "Status": "Failed - Insufficient Funds",
                    })
        if not data:
            return pd.DataFrame(columns=["Date", "Type", "Amount", "Status"])
        return pd.DataFrame(data).sort_values("Date", ascending=False)

    # ── Portfolio helpers ─────────────────────────────────────────────────────
    def get_portfolio_kpis(self):
        total = len(self.customers)
        risks = [info["base_risk"] for info in self.customers.values()]
        elasticities = [self.calculate_elasticity_score(cid) for cid in self.customers]
        avg_risk = round(float(np.mean(risks)) * 100, 1)
        avg_elasticity = round(float(np.mean(elasticities)), 2)
        # Active alerts = customers with risk > 0.6
        active_alerts = sum(1 for r in risks if r > 0.6)
        return {
            "total_customers": total,
            "avg_risk_score": avg_risk,
            "avg_elasticity_score": avg_elasticity,
            "active_alerts_today": active_alerts,
        }

    def get_portfolio_behavioral_signals(self):
        """Aggregate behavioral signals across all customers for landing page."""
        signals = {
            "salary_delays": 0,
            "savings_decline": 0,
            "upi_lending_spikes": 0,
            "failed_auto_debits": 0,
            "high_atm_withdrawals": 0,
            "utility_missed": 0,
        }
        for cid, info in self.customers.items():
            br = info["base_risk"]
            signals["salary_delays"] += 1 if br > 0.4 else 0
            signals["savings_decline"] += 1 if br > 0.5 else 0
            signals["upi_lending_spikes"] += 1 if br > 0.55 else 0
            signals["failed_auto_debits"] += 1 if br > 0.45 else 0
            signals["high_atm_withdrawals"] += 1 if br > 0.65 else 0
            signals["utility_missed"] += 1 if br > 0.6 else 0
        return signals

    def get_portfolio_predictive_forecast(self):
        """Portfolio-level default probability forecast for next 4 weeks."""
        risks = [info["base_risk"] for info in self.customers.values()]
        avg = float(np.mean(risks))
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

    def get_region_delinquency_data(self):
        """Region-wise delinquency distribution."""
        region_data = {}
        for cid, info in self.customers.items():
            region = info.get("region", "Unknown")
            risk = info["base_risk"]
            if region not in region_data:
                region_data[region] = {"count": 0, "delinquent": 0, "risk_sum": 0.0}
            region_data[region]["count"] += 1
            region_data[region]["risk_sum"] += risk
            if risk > 0.4:
                region_data[region]["delinquent"] += 1

        result = []
        for region, d in region_data.items():
            result.append({
                "region": region,
                "total_customers": d["count"],
                "delinquent_customers": d["delinquent"],
                "avg_risk_score": round(d["risk_sum"] / d["count"] * 100, 1),
            })
        result.sort(key=lambda x: x["delinquent_customers"], reverse=True)
        return result

    # ── Environment insights ──────────────────────────────────────────────────
    def get_environment_insights(self, customer_id):
        info = self.customers.get(customer_id, {})
        env = info.get("environment", "urban")
        insights = []
        if env == "rural":
            insights.append("Rural location: Cash flow likely seasonal (harvest cycles).")
            insights.append("Higher reliance on cash transactions expected.")
        elif env == "semi-urban":
            insights.append("Semi-urban: Mixed digital/cash usage pattern.")
            insights.append("Moderate sensitivity to local economic shifts.")
        elif env == "urban":
            insights.append("Urban: High digital adoption, expect consistent salary credits.")
            insights.append("Cost of living stress is a key risk factor.")
        elif env == "metro":
            insights.append("Metro: Tech-savvy, heavy UPI/Credit Card usage.")
            insights.append("High lifestyle expenses, check discretionary spend.")
        if info.get("income_stability") in ("low", "very_low"):
            insights.append("Low income stability detected: Suggest flexible payment dates.")
        return insights

    # ── Today's alerts (portfolio) ────────────────────────────────────────────
    def get_todays_alerts(self):
        return {
            "alerts": [
                {"type": "critical", "message": "5 auto-debits failed today", "count": 5},
                {"type": "warning", "message": "12 customers moved to High Risk segment", "count": 12},
                {"type": "info", "message": "Salary credits delayed for 8 accounts", "count": 8},
            ],
            "recommendations": [
                "Contact 3 critical risk customers for payment plan",
                "Review 5 new high-value transaction alerts",
                "Approve 2 hardship requests pending review",
            ],
        }
