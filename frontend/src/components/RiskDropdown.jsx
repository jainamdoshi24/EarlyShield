import { useState, useEffect } from 'react'
import { FormControl, InputLabel, Select, MenuItem, CircularProgress, Chip, Box } from '@mui/material'
import { portfolioAPI } from '../api/client'

const SEGMENT_LABELS = {
    '0-20%': '0–20% Low Delinquent',
    '20-40%': '20–40% Moderate Delinquent',
    '40-60%': '40–60% Delinquent',
    '60-80%': '60–80% High Risk',
    '80%+': '80%+ Extremely High',
}

const SEGMENT_COLORS = {
    '0-20%': '#22c55e',
    '20-40%': '#3b82f6',
    '40-60%': '#f59e0b',
    '60-80%': '#f97316',
    '80%+': '#ef4444',
}

export default function RiskDropdown({ value, onChange }) {
    const [segments, setSegments] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadSegments()
    }, [])

    const loadSegments = async () => {
        try {
            setLoading(true)
            const data = await portfolioAPI.getSegments()
            // data is { "0-20%": count, "20-40%": count, ... }
            setSegments(data)
        } catch (err) {
            console.error('Failed to load segments:', err)
            // Fallback to empty counts
            setSegments({
                '0-20%': 0,
                '20-40%': 0,
                '40-60%': 0,
                '60-80%': 0,
                '80%+': 0,
            })
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 1 }}>
                <CircularProgress size={20} />
                <span style={{ color: '#718096', fontSize: '0.85rem' }}>Loading risk segments…</span>
            </Box>
        )
    }

    const bucketKeys = ['0-20%', '20-40%', '40-60%', '60-80%', '80%+']

    return (
        <Box>
            <FormControl fullWidth>
                <InputLabel id="risk-segment-label">Select Risk Segment</InputLabel>
                <Select
                    labelId="risk-segment-label"
                    value={value}
                    label="Select Risk Segment"
                    onChange={(e) => onChange(e.target.value)}
                    sx={{ fontSize: '0.95rem' }}
                >
                    {bucketKeys.map((bucket) => {
                        const count = segments?.[bucket] ?? 0
                        const label = SEGMENT_LABELS[bucket] || bucket
                        return (
                            <MenuItem key={bucket} value={bucket}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                                    <span style={{ flex: 1 }}>{label}</span>
                                    <Chip
                                        label={count}
                                        size="small"
                                        sx={{
                                            fontWeight: 700,
                                            fontSize: '0.72rem',
                                            bgcolor: `${SEGMENT_COLORS[bucket]}18`,
                                            color: SEGMENT_COLORS[bucket],
                                            border: `1px solid ${SEGMENT_COLORS[bucket]}40`,
                                            minWidth: 30,
                                            height: 22,
                                        }}
                                    />
                                </Box>
                            </MenuItem>
                        )
                    })}
                </Select>
            </FormControl>
        </Box>
    )
}
