import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchDashboardSummary = createAsyncThunk(
    'payroll/fetchDashboardSummary',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/dashboard/summary');
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard summary');
        }
    }
);

export const importEmployees = createAsyncThunk(
    'payroll/importEmployees',
    async (file, { rejectWithValue }) => {
        try {
            const formData = new FormData();
            formData.append('file', file);
            const response = await api.post('/employees/import', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.message || 'Failed to import employees');
        }
    }
);

const initialState = {
  summary: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  importStatus: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  importError: null,
};

const payrollSlice = createSlice({
  name: 'payroll',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
        .addCase(fetchDashboardSummary.pending, (state) => {
            state.status = 'loading';
        })
        .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
            state.status = 'succeeded';
            state.summary = action.payload;
        })
        .addCase(fetchDashboardSummary.rejected, (state, action) => {
            state.status = 'failed';
            state.error = action.payload;
        })
        .addCase(importEmployees.pending, (state) => {
            state.importStatus = 'loading';
            state.importError = null;
        })
        .addCase(importEmployees.fulfilled, (state, action) => {
            state.importStatus = 'succeeded';
            // Optionally, you can trigger a refresh of dashboard data here
        })
        .addCase(importEmployees.rejected, (state, action) => {
            state.importStatus = 'failed';
            state.importError = action.payload;
        });
  }
});

export default payrollSlice.reducer; 