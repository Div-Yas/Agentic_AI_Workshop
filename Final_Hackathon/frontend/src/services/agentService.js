import api from './api';

export const agentService = {
  parseContract: (file) => api.post('/agents/contract-reader', file),
  calculateSalary: (data) => api.post('/agents/salary-breakdown', data),
  validateCompliance: (data) => api.post('/agents/compliance-mapper', data),
  detectAnomalies: (data) => api.post('/agents/anomaly-detector', data),
  generatePaystub: (data) => api.post('/agents/paystub-generator', data)
}; 