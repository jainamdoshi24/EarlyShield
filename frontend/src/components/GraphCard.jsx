import { Box, Typography } from '@mui/material'
import {
    LineChart, Line, BarChart, Bar, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot
} from 'recharts'

const CHART_COLORS = {
    blue: '#0078d4',
    indigo: '#6366f1',
    green: '#16a34a',
    teal: '#0891b2',
    yellow: '#eab308',
    orange: '#f97316',
    red: '#ef4444',
    purple: '#8b5cf6',
    rose: '#e11d48',
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

export default function GraphCard({
    title, data, type = 'line', dataKey, xKey,
    color = 'blue', height = 220, escalationIndices = []
}) {
    const chartColor = CHART_COLORS[color] || CHART_COLORS.blue

    return (
        <Box className="graph-card">
            <Typography className="graph-card-title">{title}</Typography>
            <ResponsiveContainer width="100%" height={height}>
                {type === 'area' ? (
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id={`grad-${color}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={chartColor} stopOpacity={0.2} />
                                <stop offset="95%" stopColor={chartColor} stopOpacity={0.02} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                        <XAxis dataKey={xKey} tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <YAxis tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Area type="monotone" dataKey={dataKey} stroke={chartColor} fill={`url(#grad-${color})`} strokeWidth={2} />
                        {escalationIndices.map(idx => (
                            data[idx] && <ReferenceDot key={idx} x={data[idx][xKey]} y={data[idx][dataKey]} r={5} fill="#ef4444" stroke="#ef4444" />
                        ))}
                    </AreaChart>
                ) : type === 'bar' ? (
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                        <XAxis dataKey={xKey} tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <YAxis tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey={dataKey} fill={chartColor} radius={[4, 4, 0, 0]} opacity={0.85} />
                    </BarChart>
                ) : (
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                        <XAxis dataKey={xKey} tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <YAxis tick={{ fill: '#4a5568', fontSize: 11 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Line type="monotone" dataKey={dataKey} stroke={chartColor} strokeWidth={2.5} dot={{ fill: chartColor, r: 3 }} />
                        {escalationIndices.map(idx => (
                            data[idx] && <ReferenceDot key={idx} x={data[idx][xKey]} y={data[idx][dataKey]} r={5} fill="#ef4444" stroke="#ef4444" />
                        ))}
                    </LineChart>
                )}
            </ResponsiveContainer>
        </Box>
    )
}
