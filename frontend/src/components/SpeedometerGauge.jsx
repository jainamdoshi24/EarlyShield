import { Box, Typography } from '@mui/material'

const COLORS = {
    green: { start: '#16a34a', end: '#15803d' },
    yellow: { start: '#eab308', end: '#ca8a04' },
    orange: { start: '#f97316', end: '#ea580c' },
    red: { start: '#ef4444', end: '#dc2626' },
}

function getColor(value, maxValue) {
    const pct = value / maxValue
    if (pct <= 0.25) return COLORS.green
    if (pct <= 0.50) return COLORS.yellow
    if (pct <= 0.75) return COLORS.orange
    return COLORS.red
}

function getInverseColor(value, maxValue) {
    const pct = value / maxValue
    if (pct >= 0.75) return COLORS.green
    if (pct >= 0.50) return COLORS.yellow
    if (pct >= 0.25) return COLORS.orange
    return COLORS.red
}

export default function SpeedometerGauge({ value, maxValue = 100, label, unit = '%', inverse = false }) {
    const clampedValue = Math.max(0, Math.min(value, maxValue))
    const percentage = clampedValue / maxValue
    const color = inverse ? getInverseColor(clampedValue, maxValue) : getColor(clampedValue, maxValue)

    // SVG arc parameters
    const cx = 100
    const cy = 95
    const r = 72
    const startAngle = -210
    const endAngle = 30
    const totalAngle = endAngle - startAngle
    const needleAngle = startAngle + percentage * totalAngle

    const polarToCartesian = (cx, cy, r, angleDeg) => {
        const rad = (angleDeg * Math.PI) / 180
        return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
    }

    const describeArc = (cx, cy, r, startA, endA) => {
        const s = polarToCartesian(cx, cy, r, startA)
        const e = polarToCartesian(cx, cy, r, endA)
        const large = endA - startA > 180 ? 1 : 0
        return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`
    }

    const needleEnd = polarToCartesian(cx, cy, r - 10, needleAngle)
    const ticks = [0, 0.25, 0.5, 0.75, 1.0]

    return (
        <Box sx={{ textAlign: 'center', p: 2 }}>
            <svg viewBox="0 0 200 130" width="100%" style={{ maxWidth: 240 }}>
                {/* Background arc */}
                <path
                    d={describeArc(cx, cy, r, startAngle, endAngle)}
                    fill="none"
                    stroke="rgba(0, 0, 0, 0.06)"
                    strokeWidth="14"
                    strokeLinecap="round"
                />

                {/* Color zones */}
                <path
                    d={describeArc(cx, cy, r, startAngle, startAngle + totalAngle * 0.25)}
                    fill="none"
                    stroke={inverse ? COLORS.red.start : COLORS.green.start}
                    strokeWidth="14"
                    strokeLinecap="round"
                    opacity="0.2"
                />
                <path
                    d={describeArc(cx, cy, r, startAngle + totalAngle * 0.25, startAngle + totalAngle * 0.5)}
                    fill="none"
                    stroke={COLORS.yellow.start}
                    strokeWidth="14"
                    strokeLinecap="round"
                    opacity="0.2"
                />
                <path
                    d={describeArc(cx, cy, r, startAngle + totalAngle * 0.5, startAngle + totalAngle * 0.75)}
                    fill="none"
                    stroke={COLORS.orange.start}
                    strokeWidth="14"
                    strokeLinecap="round"
                    opacity="0.2"
                />
                <path
                    d={describeArc(cx, cy, r, startAngle + totalAngle * 0.75, endAngle)}
                    fill="none"
                    stroke={inverse ? COLORS.green.start : COLORS.red.start}
                    strokeWidth="14"
                    strokeLinecap="round"
                    opacity="0.2"
                />

                {/* Active arc */}
                <path
                    d={describeArc(cx, cy, r, startAngle, needleAngle)}
                    fill="none"
                    stroke={color.start}
                    strokeWidth="14"
                    strokeLinecap="round"
                    style={{
                        filter: `drop-shadow(0 0 4px ${color.start}40)`,
                        transition: 'all 0.8s ease-out'
                    }}
                />

                {/* Tick marks */}
                {ticks.map((t, i) => {
                    const angle = startAngle + t * totalAngle
                    const outer = polarToCartesian(cx, cy, r + 8, angle)
                    const inner = polarToCartesian(cx, cy, r + 2, angle)
                    return (
                        <line
                            key={i}
                            x1={inner.x} y1={inner.y}
                            x2={outer.x} y2={outer.y}
                            stroke="rgba(0, 0, 0, 0.15)"
                            strokeWidth="1.5"
                        />
                    )
                })}

                {/* Needle */}
                <line
                    x1={cx} y1={cy}
                    x2={needleEnd.x} y2={needleEnd.y}
                    stroke={color.start}
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    style={{
                        filter: `drop-shadow(0 0 3px ${color.start}60)`,
                        transition: 'all 0.8s ease-out'
                    }}
                />

                {/* Center circle */}
                <circle cx={cx} cy={cy} r="5" fill={color.start} />
                <circle cx={cx} cy={cy} r="2.5" fill="#ffffff" />

                {/* Value text */}
                <text
                    x={cx} y={cy + 24}
                    textAnchor="middle"
                    fill={color.start}
                    fontSize="22"
                    fontWeight="800"
                    fontFamily="Inter, sans-serif"
                >
                    {typeof value === 'number' ? value.toFixed(1) : value}{unit}
                </text>
            </svg>
            <Typography
                variant="body2"
                sx={{
                    color: 'var(--text-secondary)',
                    fontWeight: 600,
                    fontSize: '0.82rem',
                    mt: -1,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                }}
            >
                {label}
            </Typography>
        </Box>
    )
}
