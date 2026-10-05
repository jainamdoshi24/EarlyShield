import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Typography
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat'

export default function CustomerTable({ customers }) {
    const navigate = useNavigate()

    const getTrendIcon = (trend) => {
        if (trend === '↑') return <TrendingUpIcon sx={{ color: '#ef4444', fontSize: 18 }} />
        if (trend === '↓') return <TrendingDownIcon sx={{ color: '#22c55e', fontSize: 18 }} />
        return <TrendingFlatIcon sx={{ color: '#a0aec0', fontSize: 18 }} />
    }

    const getRiskColor = (score) => {
        if (score >= 80) return '#ef4444'
        if (score >= 60) return '#f97316'
        if (score >= 40) return '#f59e0b'
        if (score >= 20) return '#3b82f6'
        return '#22c55e'
    }

    if (!customers || customers.length === 0) {
        return (
            <Typography variant="body2" sx={{ color: 'var(--text-muted)', textAlign: 'center', py: 4 }}>
                No customers found in this segment
            </Typography>
        )
    }

    return (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>Customer ID</TableCell>
                        <TableCell>Customer Name</TableCell>
                        <TableCell>Risk Score (%)</TableCell>
                        <TableCell>Elasticity Score</TableCell>
                        <TableCell>Last Alert</TableCell>
                        <TableCell>Risk Trend</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {customers.map((customer) => (
                        <TableRow
                            key={customer.id}
                            hover
                            onClick={() => navigate(`/customers/${customer.id}`)}
                            sx={{ cursor: 'pointer' }}
                        >
                            <TableCell>
                                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.82rem' }}>
                                    {customer.id}
                                </Typography>
                            </TableCell>
                            <TableCell>
                                <Typography
                                    variant="body2"
                                    sx={{
                                        fontWeight: 600,
                                        color: '#3b82f6 !important',
                                        cursor: 'pointer',
                                        '&:hover': { textDecoration: 'underline' }
                                    }}
                                >
                                    {customer.name}
                                </Typography>
                            </TableCell>
                            <TableCell>
                                <Chip
                                    label={`${customer.risk_score}%`}
                                    size="small"
                                    sx={{
                                        bgcolor: `${getRiskColor(customer.risk_score)}20`,
                                        color: getRiskColor(customer.risk_score),
                                        fontWeight: 700,
                                        border: `1px solid ${getRiskColor(customer.risk_score)}40`
                                    }}
                                />
                            </TableCell>
                            <TableCell>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {customer.elasticity_score}
                                </Typography>
                            </TableCell>
                            <TableCell>
                                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'var(--text-secondary) !important', maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {customer.last_alert}
                                </Typography>
                            </TableCell>
                            <TableCell>{getTrendIcon(customer.trend)}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
