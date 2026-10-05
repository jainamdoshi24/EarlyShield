import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import CustomerDetail from './pages/CustomerDetail'
import ChatbotWidget from './components/ChatbotWidget'
import Box from '@mui/material/Box'

function App() {
    return (
        <Box className="app">
            <Navbar />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/customers/:id" element={<CustomerDetail />} />
            </Routes>
            {/* Sticky context-aware chatbot — always visible */}
            <ChatbotWidget />
        </Box>
    )
}

export default App
