import { useState, useEffect } from 'react'
import { Container, Box, Typography, Grid, CircularProgress, Chip } from '@mui/material'
import RiskDropdown from '../components/RiskDropdown'
import CustomerTable from '../components/CustomerTable'
import { portfolioAPI, customerAPI } from '../api/client'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line, Legend, Cell
} from 'recharts'

// ── Colour palette ────────────────────────────────────────────────────────────
const SIGNAL_COLORS = ['#ef4444', '#f97316', '#8b5cf6', '#e11d48', '#0891b2', '#eab308']
const FORECAST_COLOR = '#0078d4'
const REGION_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#0891b2', '#8b5cf6', '#e11d48', '#14b8a6', '#6366f1', '#f43f5e']

// ── Custom tooltip ────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div className="custom-tooltip">
            <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.5 }}>{label}</Typography>
            {payload.map((p, i) => (
                <Typography key={i} variant="body2" sx={{ color: p.color || p.fill }}>
                    {p.name}: {p.value}{p.name?.includes('Risk') || p.name?.includes('Prob') ? '%' : ''}
                </Typography>
            ))}
        </div>
    )
}

// ── Metric card ───────────────────────────────────────────────────────────────
function MetricCard({ label, value, sub, color, icon }) {
    return (
        <Box sx={{
            bgcolor: '#fff',
            borderRadius: 'var(--radius)',
            border: '1px solid rgba(0,0,0,0.08)',
            boxShadow: 'var(--shadow-card)',
            p: 2.5,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
            transition: 'box-shadow 0.25s',
            '&:hover': { boxShadow: 'var(--shadow-hover)' }
        }}>
            <Typography variant="caption" sx={{ color: '#4a5568 !important', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
                {icon} {label}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: `${color} !important`, lineHeight: 1.1 }}>
                {value}
            </Typography>
            {sub && <Typography variant="caption" sx={{ color: '#718096 !important' }}>{sub}</Typography>}
        </Box>
    )
}

// ── Graph card wrapper ────────────────────────────────────────────────────────
function GraphPanel({ title, subtitle, children, loading }) {
    return (
        <Box sx={{
            bgcolor: '#fff',
            borderRadius: 'var(--radius)',
            border: '1px solid rgba(0,0,0,0.08)',
            boxShadow: 'var(--shadow-card)',
            p: 2.5,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            transition: 'box-shadow 0.25s',
            '&:hover': { boxShadow: 'var(--shadow-hover)' }
        }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.3, color: '#1a202c !important' }}>{title}</Typography>
            {subtitle && <Typography variant="caption" sx={{ color: '#718096 !important', mb: 1.5, display: 'block' }}>{subtitle}</Typography>}
            {loading ? (
                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <CircularProgress size={28} />
                </Box>
            ) : children}
        </Box>
    )
}

export default function Home() {
    const [selectedSegment, setSelectedSegment] = useState('')
    const [customers, setCustomers] = useState([])
    const [loadingCustomers, setLoadingCustomers] = useState(false)

    // Portfolio KPIs
    const [kpis, setKpis] = useState(null)
    // Three landing graphs
    const [behavioralSignals, setBehavioralSignals] = useState(null)
    const [predictiveForecast, setPredictiveForecast] = useState(null)
    const [regionData, setRegionData] = useState(null)

    useEffect(() => {
        loadPortfolioData()
    }, [])

    useEffect(() => {
        if (selectedSegment) loadCustomers(selectedSegment)
        else setCustomers([])
    }, [selectedSegment])

    const loadPortfolioData = async () => {
        try {
            const [kpiData, signals, forecast, regions] = await Promise.all([
                portfolioAPI.getKpis(),
                portfolioAPI.getBehavioralSignals(),
                portfolioAPI.getPredictiveForecast(),
                portfolioAPI.getRegionDelinquency(),
            ])
            setKpis(kpiData)
            setBehavioralSignals(signals)
            setPredictiveForecast(forecast)
            setRegionData(regions)
        } catch (err) {
            console.error('Failed to load portfolio data:', err)
        }
    }

    const loadCustomers = async (segment) => {
        try {
            setLoadingCustomers(true)
            const data = await customerAPI.getCustomers(segment)
            setCustomers(data)
        } catch (err) {
            console.error('Failed to load customers:', err)
        } finally {
            setLoadingCustomers(false)
        }
    }

    // ── Prepare chart data ────────────────────────────────────────────────────
    const signalChartData = behavioralSignals
        ? behavioralSignals.labels.map((label, i) => ({
            name: label,
            Customers: behavioralSignals.values[i],
            fill: behavioralSignals.colors[i],
        }))
        : []

    const forecastChartData = predictiveForecast
        ? predictiveForecast.weeks.map((w, i) => ({
            week: w,
            'Avg Default Prob (%)': predictiveForecast.avg_default_probability[i],
        }))
        : []

    const regionChartData = regionData
        ? regionData.regions.map((r, i) => ({
            region: r,
            Delinquent: regionData.delinquent_customers[i],
            'Avg Risk (%)': regionData.avg_risk_scores[i],
        }))
        : []

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 6 }}>
            {/* ── Page header ── */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 800, letterSpacing: '-0.02em', mb: 0.5 }}>
                    Portfolio Risk Overview
                </Typography>
                <Typography variant="body2" sx={{ color: '#4a5568 !important' }}>
                    Real-time pre-delinquency monitoring powered by Early AI
                </Typography>
            </Box>

            {/* ── KPI Cards ── */}
            <Grid container spacing={2.5} sx={{ mb: 3.5 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <MetricCard
                        label="Total Customers"
                        value={kpis ? kpis.total_customers : '—'}
                        sub="Monitored accounts"
                        color="#0078d4"
                        icon="👥"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <MetricCard
                        label="Avg Risk Score"
                        value={kpis ? `${kpis.avg_risk_score}%` : '—'}
                        sub="Portfolio average stress"
                        color="#ef4444"
                        icon="📊"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <MetricCard
                        label="Avg Elasticity Score"
                        value={kpis ? `${kpis.avg_elasticity_score}` : '—'}
                        sub="Repayment resilience (0–2)"
                        color="#16a34a"
                        icon="🔋"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <MetricCard
                        label="Active Alerts Today"
                        value={kpis ? kpis.active_alerts_today : '—'}
                        sub="High-risk triggers"
                        color="#f97316"
                        icon="🔔"
                    />
                </Grid>
            </Grid>

            {/* ── Three side-by-side graphs ── */}
            <Grid container spacing={2.5} sx={{ mb: 4 }}>
                {/* 1. Data Analytics Graph */}
                <Grid item xs={12} md={4}>
                    <GraphPanel
                        title="📡 Data Analytics"
                        subtitle="Multi-source behavioral signals — portfolio level"
                        loading={!behavioralSignals}
                    >
                        <ResponsiveContainer width="100%" height={260}>
                            <BarChart data={signalChartData} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#4a5568' }} angle={-30} textAnchor="end" interval={0} />
                                <YAxis tick={{ fontSize: 11, fill: '#4a5568' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="Customers" radius={[4, 4, 0, 0]}>
                                    {signalChartData.map((entry, index) => (
                                        <Cell key={index} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                            {signalChartData.map((d, i) => (
                                <Chip key={i} label={`${d.name}: ${d.Customers}`} size="small"
                                    sx={{ fontSize: '0.68rem', bgcolor: `${d.fill}18`, color: d.fill, fontWeight: 600, border: `1px solid ${d.fill}40` }} />
                            ))}
                        </Box>
                    </GraphPanel>
                </Grid>

                {/* 2. Predictive Analytics Graph */}
                <Grid item xs={12} md={4}>
                    <GraphPanel
                        title="🔮 Predictive Analytics"
                        subtitle="Portfolio default probability forecast — next 4 weeks"
                        loading={!predictiveForecast}
                    >
                        <ResponsiveContainer width="100%" height={260}>
                            <LineChart data={forecastChartData} margin={{ top: 4, right: 16, left: -20, bottom: 4 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                                <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#4a5568' }} />
                                <YAxis tick={{ fontSize: 11, fill: '#4a5568' }} domain={['auto', 'auto']} />
                                <Tooltip content={<CustomTooltip />} />
                                <Line
                                    type="monotone"
                                    dataKey="Avg Default Prob (%)"
                                    stroke={FORECAST_COLOR}
                                    strokeWidth={2.5}
                                    dot={{ r: 5, fill: FORECAST_COLOR }}
                                    activeDot={{ r: 7 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                        {predictiveForecast && (
                            <Box sx={{ display: 'flex', gap: 1.5, mt: 1, flexWrap: 'wrap' }}>
                                <Chip label={`High Risk: ${predictiveForecast.high_risk_count}`} size="small"
                                    sx={{ bgcolor: '#fff3e0', color: '#f97316', fontWeight: 700, fontSize: '0.7rem' }} />
                                <Chip label={`Critical: ${predictiveForecast.critical_count}`} size="small"
                                    sx={{ bgcolor: '#fef2f2', color: '#ef4444', fontWeight: 700, fontSize: '0.7rem' }} />
                                <Chip label={`Total: ${predictiveForecast.total}`} size="small"
                                    sx={{ bgcolor: '#eff6ff', color: '#0078d4', fontWeight: 700, fontSize: '0.7rem' }} />
                            </Box>
                        )}
                    </GraphPanel>
                </Grid>

                {/* 3. Environment-Aware Analysis Graph */}
                <Grid item xs={12} md={4}>
                    <GraphPanel
                        title="🌍 Environment-Aware Analysis"
                        subtitle="Top 5 regions by delinquent customer count (model-scored)"
                        loading={!regionData}
                    >
                        <ResponsiveContainer width="100%" height={260}>
                            <BarChart data={regionChartData} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                                <XAxis dataKey="region" tick={{ fontSize: 10, fill: '#4a5568' }} angle={-30} textAnchor="end" interval={0} />
                                <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#4a5568' }} />
                                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#0891b2' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend wrapperStyle={{ fontSize: '0.72rem', paddingTop: '4px' }} />
                                <Bar yAxisId="left" dataKey="Delinquent" radius={[4, 4, 0, 0]} name="Delinquent">
                                    {regionChartData.map((_, i) => (
                                        <Cell key={i} fill={REGION_COLORS[i % REGION_COLORS.length]} />
                                    ))}
                                </Bar>
                                <Line yAxisId="right" type="monotone" dataKey="Avg Risk (%)" stroke="#0891b2" strokeWidth={2} dot={{ r: 3 }} />
                            </BarChart>
                        </ResponsiveContainer>
                    </GraphPanel>
                </Grid>
            </Grid>

            {/* ── Risk Segment Selector + Customer Table ── */}
            <Box sx={{ bgcolor: '#fff', borderRadius: 'var(--radius)', border: '1px solid rgba(0,0,0,0.08)', boxShadow: 'var(--shadow-card)', p: 3 }}>
                <Typography className="section-title" sx={{ mb: 2 }}>
                    Customer Risk Segments
                </Typography>
                <Typography variant="caption" sx={{ color: '#718096 !important', display: 'block', mb: 2 }}>
                    Select a risk bucket to view and drill into customer profiles
                </Typography>
                <RiskDropdown value={selectedSegment} onChange={setSelectedSegment} />

                {selectedSegment && (
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: '#1a202c !important' }}>
                            Customers — {selectedSegment}
                        </Typography>
                        {loadingCustomers ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                                <CircularProgress size={32} />
                            </Box>
                        ) : (
                            <CustomerTable customers={customers} />
                        )}
                    </Box>
                )}
            </Box>
        </Container>
    )
}
