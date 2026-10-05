/**
 * Axios API client for backend communication
 */
import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export default apiClient;

// Portfolio API
export const portfolioAPI = {
    getSegments: () => apiClient.get('/portfolio/segments'),
    getDistribution: () => apiClient.get('/portfolio/distribution'),
    getKpis: () => apiClient.get('/portfolio/kpis'),
    getBehavioralSignals: () => apiClient.get('/portfolio/behavioral-signals'),
    getPredictiveForecast: () => apiClient.get('/portfolio/predictive-forecast'),
    getRegionDelinquency: () => apiClient.get('/portfolio/region-delinquency'),
};

// Customer API
export const customerAPI = {
    getCustomers: (segment) => apiClient.get(`/customers${segment ? `?segment=${encodeURIComponent(segment)}` : ''}`),
    getCustomer: (id) => apiClient.get(`/customers/${id}`),
    getGraphs: (id) => apiClient.get(`/customers/${id}/graphs`),
    getAlerts: (id) => apiClient.get(`/customers/${id}/alerts`),
    getSummary: (id) => apiClient.get(`/customers/${id}/summary`),
    getPredictive: (id) => apiClient.get(`/customers/${id}/predictive`),
    getEnvironment: (id) => apiClient.get(`/customers/${id}/environment`),
    getFailedPayments: (id) => apiClient.get(`/customers/${id}/failed-payments`),
    chat: (id, query) => apiClient.post(`/customers/${id}/chat`, { query }),
};
