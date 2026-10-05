import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    Container, Box, Typography, Grid, Chip, Button, Divider,
    CircularProgress, Card, CardContent
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import ShowChartIcon from '@mui/icons-material/ShowChart'

import SpeedometerGauge from '../components/SpeedometerGauge'
import GraphCard from '../components/GraphCard'
import AlertPanel from '../components/AlertPanel'
import SummaryCard from '../components/SummaryCard'
import { customerAPI } from '../api/client'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line, ReferenceLine
} from 'recharts'

const RISK_CLASS_COLORS = {
    Stable: '#16a34a',
    Emerging: '#eab308',
    Escalating: '#ea580c',
    Critical: '#dc2626'
}

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div className="custom-tooltip">
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>{label}</Typography>
            {payload.map((p, i) => (
                <Typography key={i} variant="body2" sx={{ color: p.color, fontSize: '0.82rem' }}>
                    {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
                </Typography>
            ))}
        </div>
    )
}

export default function CustomerDetail() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [customer, setCustomer] = useState(null)
    const [graphs, setGraphs] = useState(null)
    const [alerts, setAlerts] = useState([])
    const [summary, setSummary] = useState(null)
    const [predictive, setPredictive] = useState(null)
    const [environment, setEnvironment] = useState(null)
    const [failedPayments, setFailedPayments] = useState(null)

    const loadAllData = useCallback(async () => {
        setLoading(true)
        try {
            const [cust, grph, alrt, summ, pred, env, fp] = await Promise.all([
                customerAPI.getCustomer(id),
                customerAPI.getGraphs(id),
                customerAPI.getAlerts(id),
                customerAPI.getSummary(id),
                customerAPI.getPredictive(id),
                customerAPI.getEnvironment(id),
                customerAPI.getFailedPayments(id),
            ])
            setCustomer(cust)
            setGraphs(grph)
            setAlerts(alrt)
            setSummary(summ)
            setPredictive(pred)
            setEnvironment(env)
            setFailedPayments(fp)
        } catch (error) {
            console.error('Failed to load customer data:', error)
        } finally {
            setLoading(false)
        }
    }, [id])

    useEffect(() => {
        loadAllData()
    }, [loadAllData])

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
                <CircularProgress />
            </Box>
        )
    }

    if (!customer) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4 }}>
                <Typography>Customer not found</Typography>
            </Container>
        )
    }

    // Prepare graph data
    const trajectoryData = graphs?.trajectory ? graphs.trajectory.weeks.map((w, i) => ({
        week: w, risk: graphs.trajectory.risk_scores[i]
    })) : []

    const salaryData = graphs?.salary_delay ? graphs.salary_delay.months.map((m, i) => ({
        month: m, days: graphs.salary_delay.days_late[i]
    })) : []

    const savingsData = graphs?.savings ? graphs.savings.weeks.map((w, i) => ({
        week: w, balance: graphs.savings.balance[i]
    })) : []

    const upiData = graphs?.upi_lending ? graphs.upi_lending.months.map((m, i) => ({
        month: m, payments: graphs.upi_lending.payments[i]
    })) : []

    const utilityData = graphs?.utility_payments ? graphs.utility_payments.months.map((m, i) => ({
        month: m, status: graphs.utility_payments.statuses[i], value: graphs.utility_payments.status_values[i]
    })) : []

    const discretionaryData = graphs?.discretionary_spend ? graphs.discretionary_spend.months.map((m, i) => ({
        month: m, amount: graphs.discretionary_spend.amount[i]
    })) : []

    const atmData = graphs?.atm_withdrawals ? graphs.atm_withdrawals.weeks.map((w, i) => ({
        week: w, amount: graphs.atm_withdrawals.amount[i]
    })) : []

    const forecastData = predictive ? predictive.weeks.map((w, i) => ({
        week: w, probability: predictive.probabilities[i]
    })) : []

    const failedPaymentFreqData = failedPayments?.rolling_frequency ?
        failedPayments.rolling_frequency.periods.map((p, i) => ({
            period: p, count: failedPayments.rolling_frequency.counts[i]
        })) : []

    const riskClassColor = RISK_CLASS_COLORS[customer.risk_class] || '#a0aec0'

    return (
        <Container maxWidth="xl" sx={{ mt: 3, mb: 4 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate(-1)}
                    sx={{ mr: 1 }}
                >
                    Back
                </Button>
                <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                        {customer.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 0.5 }}>
                        <Chip
                            label={customer.risk_class}
                            size="small"
                            sx={{
                                bgcolor: `${riskClassColor}15`,
                                color: riskClassColor,
                                fontWeight: 700,
                                border: `1px solid ${riskClassColor}30`
                            }}
                        />
                        <Typography variant="body2" sx={{ color: '#4a5568 !important', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <LocationOnIcon sx={{ fontSize: 14 }} /> {customer.location}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#4a5568 !important', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <AccountBalanceIcon sx={{ fontSize: 14 }} /> {customer.income_stability?.replace('_', ' ')}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontFamily: 'monospace' }}>
                            ID: {customer.id}
                        </Typography>
                    </Box>
                </Box>
            </Box>

            {/* Row 1: Gauges + Summary */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
                            <SpeedometerGauge
                                value={customer.risk_score}
                                maxValue={100}
                                label="Financial Stress"
                                unit="%"
                            />
                            <SpeedometerGauge
                                value={customer.elasticity_score}
                                maxValue={2}
                                label="Elasticity"
                                unit=""
                                inverse={true}
                            />
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <SummaryCard summary={summary} />
                </Grid>
                <Grid item xs={12} md={4}>
                    <AlertPanel alerts={alerts} />
                </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {/* Row 2: Risk Trajectory (full width) */}
            <Typography className="section-title" sx={{ mb: 2 }}>
                <ShowChartIcon sx={{ fontSize: 20, color: '#0078d4' }} /> Risk Trajectory
            </Typography>
            <GraphCard
                title="Risk Score Over Time (%)"
                data={trajectoryData}
                type="area"
                dataKey="risk"
                xKey="week"
                color="teal"
                height={260}
                escalationIndices={graphs?.trajectory?.escalation_indices || []}
            />

            <Divider sx={{ my: 3 }} />

            {/* Row 3: Multi-Source Analytics (3x2 grid) */}
            <Typography className="section-title" sx={{ mb: 2 }}>
                Multi-Source Analytics
            </Typography>
            <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                    <GraphCard
                        title="Salary Credit Delays (Days)"
                        data={salaryData}
                        type="bar"
                        dataKey="days"
                        xKey="month"
                        color="orange"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <GraphCard
                        title="Savings Balance Trend (₹)"
                        data={savingsData}
                        type="area"
                        dataKey="balance"
                        xKey="week"
                        color="teal"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <GraphCard
                        title="UPI to Lending Apps"
                        data={upiData}
                        type="bar"
                        dataKey="payments"
                        xKey="month"
                        color="purple"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <GraphCard
                        title="Discretionary Spending (₹)"
                        data={discretionaryData}
                        type="line"
                        dataKey="amount"
                        xKey="month"
                        color="yellow"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <GraphCard
                        title="ATM Withdrawal Pattern (₹)"
                        data={atmData}
                        type="bar"
                        dataKey="amount"
                        xKey="week"
                        color="rose"
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <Box className="graph-card">
                        <Typography className="graph-card-title">Utility Payments Status</Typography>
                        <ResponsiveContainer width="100%" height={220}>
                            <BarChart data={utilityData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                                <XAxis dataKey="month" tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                                <YAxis
                                    ticks={[0, 1, 2]}
                                    tickFormatter={v => ['On Time', 'Late', 'Missed'][v] || ''}
                                    tick={{ fill: '#4a5568', fontSize: 10 }}
                                    axisLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                                />
                                <Tooltip content={({ active, payload, label }) => {
                                    if (!active || !payload?.length) return null
                                    const status = ['On Time', 'Late', 'Missed'][payload[0].value] || 'Unknown'
                                    return (
                                        <div className="custom-tooltip">
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{label}</Typography>
                                            <Typography variant="body2" sx={{ color: status === 'On Time' ? '#16a34a' : status === 'Late' ? '#eab308' : '#dc2626' }}>
                                                {status}
                                            </Typography>
                                        </div>
                                    )
                                }} />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {utilityData.map((entry, index) => {
                                        const color = entry.value === 0 ? '#16a34a' : entry.value === 1 ? '#eab308' : '#dc2626'
                                        return <Bar key={index} fill={color} />
                                    })}
                                </Bar>
                                <ReferenceLine y={1} stroke="#eab308" strokeDasharray="3 3" opacity={0.4} />
                            </BarChart>
                        </ResponsiveContainer>
                    </Box>
                </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {/* Row 4: Predictive + Failed Payments + Environment */}
            <Typography className="section-title" sx={{ mb: 2 }}>
                Predictive Analytics & Monitoring
            </Typography>
            <Grid container spacing={2}>
                {/* Predictive Forecast */}
                <Grid item xs={12} md={4}>
                    <Box className="graph-card">
                        <Typography className="graph-card-title">Default Probability Forecast</Typography>
                        {predictive && (
                            <>
                                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                                    <Box>
                                        <Typography variant="caption" sx={{ color: '#a0aec0', fontSize: '0.68rem' }}>Class</Typography>
                                        <Chip
                                            label={predictive.class_label}
                                            size="small"
                                            sx={{
                                                display: 'block',
                                                mt: 0.3,
                                                bgcolor: `${RISK_CLASS_COLORS[predictive.class_label] || '#a0aec0'}15`,
                                                color: RISK_CLASS_COLORS[predictive.class_label] || '#a0aec0',
                                                fontWeight: 700
                                            }}
                                        />
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" sx={{ color: '#a0aec0', fontSize: '0.68rem' }}>Trend</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.3, textTransform: 'capitalize' }}>
                                            {predictive.trend}
                                        </Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" sx={{ color: '#a0aec0', fontSize: '0.68rem' }}>Elasticity</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.3 }}>{predictive.elasticity}</Typography>
                                    </Box>
                                </Box>
                                <ResponsiveContainer width="100%" height={160}>
                                    <LineChart data={forecastData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                                        <XAxis dataKey="week" tick={{ fill: '#4a5568', fontSize: 10 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                                        <YAxis tick={{ fill: '#4a5568', fontSize: 10 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} domain={[0, 100]} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <ReferenceLine y={60} stroke="#ea580c" strokeDasharray="3 3" opacity={0.5} />
                                        <ReferenceLine y={80} stroke="#dc2626" strokeDasharray="3 3" opacity={0.5} />
                                        <Line type="monotone" dataKey="probability" stroke="#6366f1" strokeWidth={2.5} dot={{ fill: '#6366f1', r: 4 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </>
                        )}
                    </Box>
                </Grid>

                {/* Failed Payments Timeline */}
                <Grid item xs={12} md={4}>
                    <Box className="graph-card">
                        <Typography className="graph-card-title">Failed Payments Monitoring</Typography>
                        {failedPayments?.timeline?.length > 0 ? (
                            <>
                                <Box sx={{ maxHeight: 120, overflowY: 'auto', mb: 2 }}>
                                    {failedPayments.timeline.slice(0, 5).map((fp, i) => (
                                        <Box key={i} sx={{
                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                            py: 0.8, borderBottom: '1px solid rgba(0,0,0,0.06)',
                                            '&:last-child': { borderBottom: 'none' }
                                        }}>
                                            <Box>
                                                <Typography variant="body2" sx={{ fontSize: '0.8rem', fontWeight: 600 }}>{fp.type}</Typography>
                                                <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem' }}>{fp.date}</Typography>
                                            </Box>
                                            <Box sx={{ textAlign: 'right' }}>
                                                <Typography variant="body2" sx={{ fontSize: '0.8rem', fontWeight: 600 }}>₹{fp.amount?.toLocaleString()}</Typography>
                                                <Chip
                                                    label={fp.status}
                                                    size="small"
                                                    sx={{
                                                        height: 18, fontSize: '0.62rem', fontWeight: 700,
                                                        bgcolor: fp.status === 'Failed' ? 'rgba(220,38,38,0.08)' : 'rgba(234,88,12,0.08)',
                                                        color: fp.status === 'Failed' ? '#dc2626' : '#ea580c'
                                                    }}
                                                />
                                            </Box>
                                        </Box>
                                    ))}
                                </Box>
                                {/* Frequency chart */}
                                <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem', fontWeight: 600, textTransform: 'uppercase' }}>
                                    Rolling Failure Frequency
                                </Typography>
                                <ResponsiveContainer width="100%" height={100}>
                                    <BarChart data={failedPaymentFreqData}>
                                        <XAxis dataKey="period" tick={{ fill: '#4a5568', fontSize: 9 }} axisLine={false} tickLine={false} />
                                        <YAxis hide />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Bar dataKey="count" fill="#dc2626" radius={[4, 4, 0, 0]} opacity={0.7} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </>
                        ) : (
                            <Typography variant="body2" sx={{ color: '#a0aec0 !important', textAlign: 'center', py: 4, fontSize: '0.85rem' }}>
                                No failed payments recorded
                            </Typography>
                        )}
                    </Box>
                </Grid>

                {/* Environment Analysis */}
                <Grid item xs={12} md={4}>
                    <Box className="graph-card" sx={{ height: '100%' }}>
                        <Typography className="graph-card-title">Environment-Aware Analysis</Typography>
                        {environment && (
                            <>
                                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                                    <Box>
                                        <Typography variant="caption" sx={{ color: '#a0aec0', fontSize: '0.68rem' }}>Type</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.3 }}>{environment.customer_type}</Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" sx={{ color: '#a0aec0', fontSize: '0.68rem' }}>Geography</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.3, textTransform: 'capitalize' }}>{environment.geography?.location}</Typography>
                                    </Box>
                                </Box>

                                {/* Channel Behavior */}
                                <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem', fontWeight: 600, textTransform: 'uppercase' }}>
                                    Channel Behavior
                                </Typography>
                                <Box sx={{ mt: 1, mb: 2 }}>
                                    {environment.channel_behavior && Object.entries(environment.channel_behavior).map(([ch, val]) => (
                                        <Box key={ch} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                            <Typography variant="caption" sx={{ width: 60, color: '#4a5568 !important', fontSize: '0.72rem' }}>{ch}</Typography>
                                            <Box sx={{ flexGrow: 1, height: 6, bgcolor: 'rgba(0,0,0,0.06)', borderRadius: 3 }}>
                                                <Box sx={{
                                                    height: '100%',
                                                    width: `${val * 100}%`,
                                                    bgcolor: val > 0.6 ? '#dc2626' : val > 0.4 ? '#eab308' : '#16a34a',
                                                    borderRadius: 3,
                                                    transition: 'width 0.8s ease'
                                                }} />
                                            </Box>
                                            <Typography variant="caption" sx={{ fontSize: '0.7rem', color: '#a0aec0 !important', width: 30, textAlign: 'right' }}>
                                                {(val * 100).toFixed(0)}%
                                            </Typography>
                                        </Box>
                                    ))}
                                </Box>

                                {/* Geo Factors */}
                                <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem', fontWeight: 600, textTransform: 'uppercase' }}>
                                    Geography Factors
                                </Typography>
                                <Box sx={{ mt: 1, mb: 1 }}>
                                    {environment.geography?.factors && Object.entries(environment.geography.factors).map(([k, v]) => (
                                        <Box key={k} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.3 }}>
                                            <Typography variant="caption" sx={{ color: '#4a5568 !important', fontSize: '0.72rem', textTransform: 'capitalize' }}>
                                                {k.replace('_', ' ')}
                                            </Typography>
                                            <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.72rem' }}>
                                                {(v * 100).toFixed(0)}%
                                            </Typography>
                                        </Box>
                                    ))}
                                </Box>

                                {/* Bias Notes */}
                                {environment.bias_safe_notes?.length > 0 && (
                                    <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(0, 120, 212, 0.04)', borderRadius: 1, border: '1px solid rgba(0,120,212,0.1)' }}>
                                        <Typography variant="caption" sx={{ color: '#4a5568 !important', fontSize: '0.65rem' }}>
                                            ⓘ {environment.bias_safe_notes[0]}
                                        </Typography>
                                    </Box>
                                )}
                            </>
                        )}
                    </Box>
                </Grid>
            </Grid>

        </Container>
    )
}
