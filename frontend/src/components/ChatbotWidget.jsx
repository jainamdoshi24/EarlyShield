/**
 * ChatbotWidget — sticky floating chat icon + overlay panel
 * Context-aware: knows which customer the banker is viewing.
 */
import { useState, useRef, useEffect } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import {
    Box, Typography, IconButton, TextField, CircularProgress, Chip
} from '@mui/material'
import { customerAPI } from '../api/client'

const BOT_AVATAR = '🤖'
const USER_AVATAR = '👤'

function formatBotText(text) {
    // Convert **bold** markdown and bullet points
    const lines = text.split('\n')
    return lines.map((line, i) => {
        const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        return <div key={i} dangerouslySetInnerHTML={{ __html: formatted || '&nbsp;' }} />
    })
}

export default function ChatbotWidget() {
    const [open, setOpen] = useState(false)
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [customerName, setCustomerName] = useState(null)
    const messagesEndRef = useRef(null)

    // Detect current customer from URL
    const location = useLocation()
    const match = location.pathname.match(/\/customers\/([^/]+)/)
    const customerId = match ? match[1] : null

    // When customer changes, update context and reset chat
    useEffect(() => {
        if (customerId) {
            // Fetch customer name for context display
            customerAPI.getCustomer(customerId)
                .then(data => setCustomerName(data.name))
                .catch(() => setCustomerName(customerId))

            // Add context message if chat is open
            if (open && messages.length === 0) {
                addWelcomeMessage(customerId)
            }
        } else {
            setCustomerName(null)
        }
    }, [customerId])

    // When chat opens, add welcome
    useEffect(() => {
        if (open && messages.length === 0) {
            if (customerId) {
                addWelcomeMessage(customerId)
            } else {
                setMessages([{
                    role: 'bot',
                    text: "👋 Hello! I'm Early AI Assistant.\n\nNavigate to a customer's detail page and I'll provide **context-aware insights** about their risk profile, signals, and recommended actions.",
                    type: 'greeting'
                }])
            }
        }
    }, [open])

    const addWelcomeMessage = (cid) => {
        setMessages([{
            role: 'bot',
            text: `👋 Hello! I'm your Early AI assistant.\n\nI'm currently viewing **${cid}**'s profile. You can ask me:\n• Why is this customer high risk?\n• What signals are contributing most?\n• What actions should the banker take?\n• Explain the predictive forecast\n• What's the elasticity score?`,
            type: 'greeting'
        }])
    }

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim()) return
        const userMsg = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', text: userMsg }])

        if (!customerId) {
            setMessages(prev => [...prev, {
                role: 'bot',
                text: "Please navigate to a **customer detail page** first. I'll then be able to answer questions about that specific customer.",
                type: 'info'
            }])
            return
        }

        setLoading(true)
        try {
            const response = await customerAPI.chat(customerId, userMsg)
            setMessages(prev => [...prev, { role: 'bot', text: response.text, type: response.type }])
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'bot',
                text: "Sorry, I couldn't process that request. Please try again.",
                type: 'error'
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    const quickQuestions = customerId ? [
        'Why is this customer high risk?',
        'What signals are contributing?',
        'What actions should I take?',
        'Explain the forecast',
    ] : []

    return (
        <>
            {/* ── Chat overlay panel ── */}
            {open && (
                <Box sx={{
                    position: 'fixed',
                    bottom: 88,
                    right: 24,
                    width: 380,
                    maxWidth: 'calc(100vw - 48px)',
                    height: 520,
                    bgcolor: '#fff',
                    borderRadius: 'var(--radius)',
                    boxShadow: '0 8px 40px rgba(0,0,0,0.18)',
                    border: '1px solid rgba(0,0,0,0.1)',
                    display: 'flex',
                    flexDirection: 'column',
                    zIndex: 1300,
                    overflow: 'hidden',
                    animation: 'slideUp 0.2s ease',
                    '@keyframes slideUp': {
                        from: { opacity: 0, transform: 'translateY(16px)' },
                        to: { opacity: 1, transform: 'translateY(0)' }
                    }
                }}>
                    {/* Header */}
                    <Box sx={{
                        background: 'linear-gradient(135deg, #00aeef, #0078d4)',
                        px: 2,
                        py: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ fontSize: '1.4rem' }}>🤖</Box>
                            <Box>
                                <Typography variant="subtitle2" sx={{ color: '#fff !important', fontWeight: 700, lineHeight: 1.2 }}>
                                    Early AI
                                </Typography>
                                {customerName && (
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.85) !important', fontSize: '0.7rem' }}>
                                        Viewing: {customerName}
                                    </Typography>
                                )}
                            </Box>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <IconButton size="small" onClick={() => { setMessages([]); if (customerId) addWelcomeMessage(customerId) }}
                                sx={{ color: 'rgba(255,255,255,0.8)', '&:hover': { color: '#fff', bgcolor: 'rgba(255,255,255,0.1)' } }}
                                title="Clear chat">
                                <span style={{ fontSize: '0.9rem' }}>🔄</span>
                            </IconButton>
                            <IconButton size="small" onClick={() => setOpen(false)}
                                sx={{ color: 'rgba(255,255,255,0.8)', '&:hover': { color: '#fff', bgcolor: 'rgba(255,255,255,0.1)' } }}>
                                <span style={{ fontSize: '1rem' }}>✕</span>
                            </IconButton>
                        </Box>
                    </Box>

                    {/* Messages */}
                    <Box className="chat-messages" sx={{ flex: 1, overflowY: 'auto', p: 1.5, display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {messages.map((msg, i) => (
                            <Box key={i} sx={{ display: 'flex', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row', gap: 0.8, alignItems: 'flex-start' }}>
                                <Box sx={{ fontSize: '1rem', mt: 0.3, flexShrink: 0 }}>
                                    {msg.role === 'user' ? USER_AVATAR : BOT_AVATAR}
                                </Box>
                                <Box className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}
                                    sx={{ fontSize: '0.82rem', lineHeight: 1.55 }}>
                                    {formatBotText(msg.text)}
                                </Box>
                            </Box>
                        ))}
                        {loading && (
                            <Box sx={{ display: 'flex', gap: 0.8, alignItems: 'center' }}>
                                <Box sx={{ fontSize: '1rem' }}>{BOT_AVATAR}</Box>
                                <Box className="chat-bubble-bot" sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                                    <CircularProgress size={12} />
                                    <Typography variant="caption" sx={{ color: '#4a5568 !important' }}>Thinking…</Typography>
                                </Box>
                            </Box>
                        )}
                        <div ref={messagesEndRef} />
                    </Box>

                    {/* Quick questions */}
                    {quickQuestions.length > 0 && messages.length <= 1 && (
                        <Box sx={{ px: 1.5, pb: 0.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {quickQuestions.map((q, i) => (
                                <Chip key={i} label={q} size="small" clickable
                                    onClick={() => { setInput(q); }}
                                    sx={{ fontSize: '0.68rem', bgcolor: '#eff6ff', color: '#0078d4', border: '1px solid #bfdbfe', fontWeight: 500, cursor: 'pointer' }} />
                            ))}
                        </Box>
                    )}

                    {/* Input */}
                    <Box sx={{ p: 1.5, borderTop: '1px solid rgba(0,0,0,0.08)', display: 'flex', gap: 1 }}>
                        <TextField
                            fullWidth
                            size="small"
                            placeholder={customerId ? "Ask about this customer…" : "Navigate to a customer first…"}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            multiline
                            maxRows={3}
                            sx={{
                                '& .MuiOutlinedInput-root': { fontSize: '0.83rem', borderRadius: '8px' },
                            }}
                        />
                        <IconButton
                            onClick={sendMessage}
                            disabled={!input.trim() || loading}
                            sx={{
                                bgcolor: '#0078d4',
                                color: '#fff',
                                borderRadius: '8px',
                                width: 38,
                                height: 38,
                                alignSelf: 'flex-end',
                                '&:hover': { bgcolor: '#0065b3' },
                                '&.Mui-disabled': { bgcolor: '#e2e8f0', color: '#a0aec0' }
                            }}>
                            <span style={{ fontSize: '1rem' }}>➤</span>
                        </IconButton>
                    </Box>
                </Box>
            )}

            {/* ── Sticky chat icon button ── */}
            <Box
                onClick={() => setOpen(prev => !prev)}
                sx={{
                    position: 'fixed',
                    bottom: 24,
                    right: 24,
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #00aeef, #0078d4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 4px 20px rgba(0, 120, 212, 0.4)',
                    zIndex: 1301,
                    transition: 'all 0.25s ease',
                    '&:hover': {
                        transform: 'scale(1.08)',
                        boxShadow: '0 6px 28px rgba(0, 120, 212, 0.55)',
                    },
                    '&:active': { transform: 'scale(0.95)' }
                }}
                title="Early AI Assistant"
            >
                <span style={{ fontSize: open ? '1.3rem' : '1.5rem', transition: 'font-size 0.2s' }}>
                    {open ? '✕' : '🤖'}
                </span>
                {/* Notification dot when on customer page */}
                {customerId && !open && (
                    <Box sx={{
                        position: 'absolute',
                        top: 6,
                        right: 6,
                        width: 10,
                        height: 10,
                        bgcolor: '#ef4444',
                        borderRadius: '50%',
                        border: '2px solid #fff',
                        animation: 'pulse 2s infinite',
                        '@keyframes pulse': {
                            '0%, 100%': { opacity: 1 },
                            '50%': { opacity: 0.5 }
                        }
                    }} />
                )}
            </Box>
        </>
    )
}
