import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Create a configured Axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // Request timeout in milliseconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * A utility function to handle API requests and standardize error handling.
 * @param {Promise} request - The Axios request promise.
 * @returns {Promise<[any, any]>} - A promise that resolves to an array: [data, error].
 */
const handleRequest = async (request) => {
  try {
    const response = await request;
    return [response.data, null];
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message;
    console.error('API Error:', errorMessage);
    return [null, errorMessage];
  }
};

// --- Employee API Functions ---

export const createEmployee = (employeeData) => {
  return handleRequest(api.post('/employees', employeeData));
};

export const getEmployeeById = (employeeId) => {
  return handleRequest(api.get(`/employees/${employeeId}`));
};

export const getEmployees = () => {
  return handleRequest(api.get('/employees'));
};

export const updateEmployee = (employeeId, employeeData) => {
  return handleRequest(api.put(`/employees/${employeeId}`, employeeData));
};

export const deleteEmployee = (employeeId) => {
  return handleRequest(api.delete(`/employees/${employeeId}`));
};


// --- Payroll API Functions ---

export const processPayroll = (payrollData) => {
  return handleRequest(api.post('/payroll/process', payrollData));
};

export const getPayrollStatus = (requestId) => {
  return handleRequest(api.get(`/payroll/${requestId}`));
};


// --- Health & Agent Info ---

export const getHealth = () => {
  return handleRequest(api.get('/health'));
};

export const listAgents = () => {
  return handleRequest(api.get('/agents'));
};

export default api; 