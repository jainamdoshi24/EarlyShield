# Early AI - Risk Dashboard

## Overview
Complete **React + FastAPI** rebuild of the Early AI pre-delinquency risk monitoring system with modular backend architecture and modern React frontend.

## Architecture

### Backend (FastAPI)
- **Port:** 8000
- **API Prefix:** `/api`
- **Structure:**
  - `engines/` - Modular business logic (scoring, graphs, alerts, summary, chatbot)
  - `routes/` - API endpoints (portfolio, customers)
  - `data/` - Data simulator
  - `models/` - ML model (earlyshield_model2.pkl)

### Frontend (React + Vite)
- **Port:** 3000
- **Tech Stack:** React 18, Material-UI, Recharts, Axios
- **Pages:**
  - Home - Risk dropdown + distribution chart
  - CustomerList - Filterable table
  - CustomerDetail - Full analytics with sidebar

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend will start at `http://localhost:8000`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will start at `http://localhost:3000`

## API Endpoints

### Portfolio
- `GET /api/portfolio/segments` - Risk segment counts
- `GET /api/portfolio/distribution` - Chart data

### Customers
- `GET /api/customers?segment={bucket}` - List customers
- `GET /api/customers/{id}` - Customer profile
- `GET /api/customers/{id}/graphs` - All graph data
- `GET /api/customers/{id}/alerts` - Customer alerts
- `GET /api/customers/{id}/summary` - Daily summary
- `POST /api/customers/{id}/chat` - Chatbot interaction

##Features

✅ **Dropdown Navigation** - 5 risk categories selector  
✅ **Customer Table** - ID, Name, Risk %, Elasticity, Alerts, Trend  
✅ **6 Signal Charts** - Salary, Savings, UPI, Spending, ATM, etc.  
✅ **ML Model Integration** - Uses earlyshield_model2.pkl  
✅ **Smart Alerts** - Severity-based prioritization  
✅ **Daily Summary** - Customer-specific recommendations  
✅ **Chatbot** - Context-aware Q&A for each customer  
✅ **Production Ready** - Debug disabled, optimized builds

## Dependencies

### Backend
- FastAPI 0.109
- Uvicorn
- Pydantic Settings
- LightGBM 4.3
- Pandas, NumPy, Scikit-learn

### Frontend
- React 18
- Material-UI 5
- Recharts 2
- Axios
- React Router 6

## Environment Variables

Create `.env` in backend/:
```
APP_NAME=EarlyShield AI
DEBUG=False
MODEL_PATH=backend/models/earlyshield_model2.pkl
```

## Deployment

### Docker (Future)
```bash
docker-compose up
```

## Old Dash Code
The previous Dash implementation is backed up in `backup_dash/` folder.

## License
Proprietary - Early AI
