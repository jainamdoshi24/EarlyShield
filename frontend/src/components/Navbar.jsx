import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import { useNavigate } from 'react-router-dom'


export default function Navbar() {
    const navigate = useNavigate()

    return (
        <AppBar position="sticky" elevation={0}>
            <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                        cursor: 'pointer',
                        flexGrow: 1
                    }}
                    onClick={() => navigate('/')}
                >
                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 800,
                            letterSpacing: '-0.02em',
                            color: '#0f172a !important',
                        }}
                    >
                        Early AI
                    </Typography>
                </Box>
                <Typography
                    variant="body2"
                    sx={{ opacity: 0.8, fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.04em', color: '#0f172a !important' }}
                >
                    PRE-DELINQUENCY RISK MONITORING
                </Typography>
            </Toolbar>
        </AppBar>
    )
}
