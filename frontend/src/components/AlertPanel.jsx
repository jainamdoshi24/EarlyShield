import { Card, CardContent, Alert, Typography, Box, Chip } from '@mui/material'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'

const severityMap = {
    critical: 'error',
    high: 'warning',
    medium: 'info',
    low: 'success'
}

const severityColors = {
    critical: '#dc2626',
    high: '#ea580c',
    medium: '#0078d4',
    low: '#16a34a'
}

export default function AlertPanel({ alerts }) {
    if (!alerts || alerts.length === 0) {
        return (
            <Card>
                <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <WarningAmberIcon sx={{ color: '#a0aec0', fontSize: 20 }} />
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Active Alerts</Typography>
                    </Box>
                    <Alert severity="success" sx={{ mt: 1 }}>No active alerts — all clear</Alert>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WarningAmberIcon sx={{ color: '#ea580c', fontSize: 20 }} />
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Active Alerts</Typography>
                    </Box>
                    <Chip
                        label={`${alerts.length} Active`}
                        size="small"
                        sx={{
                            bgcolor: 'rgba(239, 68, 68, 0.1)',
                            color: '#dc2626',
                            fontWeight: 600,
                            fontSize: '0.72rem'
                        }}
                    />
                </Box>
                {alerts.map((alert, i) => (
                    <Alert
                        key={i}
                        severity={severityMap[alert.severity] || 'info'}
                        sx={{ mb: 1, '& .MuiAlert-message': { width: '100%' } }}
                    >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                            <Box>
                                <Chip
                                    label={alert.severity.toUpperCase()}
                                    size="small"
                                    sx={{
                                        bgcolor: `${severityColors[alert.severity]}15`,
                                        color: severityColors[alert.severity],
                                        fontWeight: 700,
                                        fontSize: '0.65rem',
                                        height: 20,
                                        mr: 1
                                    }}
                                />
                                <Typography component="span" variant="body2" sx={{ fontSize: '0.82rem' }}>
                                    {alert.message}
                                </Typography>
                            </Box>
                            {alert.timestamp && (
                                <Typography variant="caption" sx={{ color: '#a0aec0 !important', ml: 1, whiteSpace: 'nowrap' }}>
                                    {alert.timestamp}
                                </Typography>
                            )}
                        </Box>
                    </Alert>
                ))}
            </CardContent>
        </Card>
    )
}
