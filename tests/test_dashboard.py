import pytest
import pandas as pd
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_simulator import CustomerDataSimulator
from chatbot import EarlyShieldChatbot

@pytest.fixture
def simulator():
    return CustomerDataSimulator()

@pytest.fixture
def chatbot(simulator):
    return EarlyShieldChatbot(simulator)

class TestDataSimulator:
    def test_risk_bucketing(self, simulator):
        """Test if risk scores are correctly classified into buckets"""
        assert simulator.get_risk_bucket(0.15) == '0-20%'
        assert simulator.get_risk_bucket(0.35) == '20-40%'
        assert simulator.get_risk_bucket(0.55) == '40-60%'
        assert simulator.get_risk_bucket(0.75) == '60-80%'
        assert simulator.get_risk_bucket(0.85) == '80%+'

    def test_customer_segmentation(self, simulator):
        """Test if customers are correctly filtered by bucket"""
        # Get a known customer
        cid = 'CUST100' # Likely Low or Moderate
        info = simulator.get_customer_info(cid)
        bucket = simulator.get_risk_bucket(info['base_risk'])
        
        # Verify they appear in that bucket list
        customers = simulator.get_customers_by_bucket(bucket)
        assert cid in customers
        
        # Verify counts match
        counts = simulator.get_risk_segment_counts()
        total_customers = sum(counts.values())
        assert total_customers == len(simulator.get_customer_list())

    def test_elasticity_calculation(self, simulator):
        """Test elasticity score logic"""
        # High risk should have lower elasticity
        high_risk_cust = 'CUST500' # Critical risk
        low_risk_cust = 'CUST100' # Low risk
        
        score_high = simulator.calculate_elasticity_score(high_risk_cust)
        score_low = simulator.calculate_elasticity_score(low_risk_cust)
        
        assert 0.0 <= score_high <= 2.0
        assert 0.0 <= score_low <= 2.0
        # Generally low risk customers have higher elasticity
        assert score_low > score_high

    def test_signal_generators(self, simulator):
        """Test if signal generation returns valid DataFrames"""
        cid = 'CUST100'
        
        df_salary = simulator.generate_salary_delay_data(cid)
        assert not df_salary.empty
        assert 'Days Late' in df_salary.columns
        
        df_upi = simulator.generate_upi_lending_data(cid)
        assert not df_upi.empty
        assert 'Payments' in df_upi.columns
        
        df_atm = simulator.generate_atm_withdrawal_data(cid)
        assert not df_atm.empty
        assert 'Amount' in df_atm.columns

class TestChatbot:
    def test_customer_query(self, chatbot):
        """Test asking for a specific customer"""
        response = chatbot.process_query("show me details for CUST100")
        assert "CUST100" in response['text']
        assert response['related_id'] == "CUST100"

    def test_risk_count_query(self, chatbot):
        """Test asking for risk counts"""
        response = chatbot.process_query("how many high risk customers")
        assert "High" in response['text'] or "Critical" in response['text']
        
    def test_alerts_query(self, chatbot):
        """Test asking for alerts"""
        response = chatbot.process_query("any alerts today?")
        assert "alerts" in response['text'].lower()

    def test_fallback(self, chatbot):
        """Test gibberish query"""
        response = chatbot.process_query("xyz pdq 123")
        assert "I'm not sure I understand" in response['text']
