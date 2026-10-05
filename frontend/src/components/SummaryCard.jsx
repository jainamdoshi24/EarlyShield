import {
    Card, CardContent, Typography, Box, Chip, Divider, List, ListItem, ListItemIcon, ListItemText
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import BuildIcon from '@mui/icons-material/Build'
import InfoIcon from '@mui/icons-material/Info'

const movementIcon = {
    up: <TrendingUpIcon sx={{ color: '#dc2626', fontSize: 18 }} />,
    down: <TrendingDownIcon sx={{ color: '#16a34a', fontSize: 18 }} />,
    stable: <TrendingFlatIcon sx={{ color: '#a0aec0', fontSize: 18 }} />,
}

const movementColor = {
    up: '#dc2626',
    down: '#16a34a',
    stable: '#a0aec0',
}

export default function SummaryCard({ summary }) {
    if (!summary) return null

    return (
        <Card>
            <CardContent>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <InfoIcon sx={{ fontSize: 18, color: '#0078d4' }} />
                    Today's Summary
                </Typography>

                {/* Risk Movement */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                    {movementIcon[summary.risk_movement] || movementIcon.stable}
                    <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                        Risk: <strong style={{ color: movementColor[summary.risk_movement] }}>
                            {summary.risk_movement?.toUpperCase()}
                        </strong>
                        {summary.risk_class && (
                            <Chip
                                label={summary.risk_class}
                                size="small"
                                sx={{
                                    ml: 1,
                                    height: 20,
                                    fontSize: '0.68rem',
                                    fontWeight: 700,
                                    bgcolor: 'rgba(0, 0, 0, 0.05)',
                                    color: '#4a5568'
                                }}
                            />
                        )}
                    </Typography>
                </Box>

                {/* Triggered Signals */}
                {summary.new_signals?.length > 0 && (
                    <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
                            Triggered Signals
                        </Typography>
                        {summary.new_signals.map((sig, i) => (
                            <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                <NotificationsActiveIcon sx={{ fontSize: 14, color: '#ea580c' }} />
                                <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{sig}</Typography>
                            </Box>
                        ))}
                    </Box>
                )}

                {/* Alerts & Failed Payments */}
                <Box sx={{ display: 'flex', gap: 2, mb: 1.5 }}>
                    <Box>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem' }}>Escalated</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700, color: summary.escalated_alerts > 0 ? '#dc2626 !important' : 'inherit' }}>
                            {summary.escalated_alerts || 0}
                        </Typography>
                    </Box>
                    <Box>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem' }}>Total Alerts</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700 }}>{summary.total_alerts || 0}</Typography>
                    </Box>
                    <Box>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontSize: '0.68rem' }}>Failed Today</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700, color: summary.failed_payments_today > 0 ? '#ea580c !important' : 'inherit' }}>
                            {summary.failed_payments_today || 0}
                        </Typography>
                    </Box>
                </Box>

                <Divider sx={{ my: 1.5 }} />

                {/* Recommendations */}
                {summary.recommendations?.length > 0 && (
                    <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
                            Recommended Actions
                        </Typography>
                        <List dense disablePadding>
                            {summary.recommendations.map((rec, i) => (
                                <ListItem key={i} disablePadding sx={{ py: 0.3 }}>
                                    <ListItemIcon sx={{ minWidth: 24 }}>
                                        <BuildIcon sx={{ fontSize: 14, color: '#0078d4' }} />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={rec}
                                        primaryTypographyProps={{ fontSize: '0.8rem' }}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}

                {/* Quick Insights */}
                {summary.quick_insights?.length > 0 && (
                    <Box>
                        <Typography variant="caption" sx={{ color: '#a0aec0 !important', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
                            Quick Insights
                        </Typography>
                        {summary.quick_insights.map((insight, i) => (
                            <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 0.5, mt: 0.5 }}>
                                <LightbulbIcon sx={{ fontSize: 14, color: '#eab308', mt: 0.3 }} />
                                <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{insight}</Typography>
                            </Box>
                        ))}
                    </Box>
                )}
            </CardContent>
        </Card>
    )
}
