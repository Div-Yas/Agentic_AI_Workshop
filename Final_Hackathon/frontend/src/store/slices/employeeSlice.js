import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Thunk for bulk employee import
export const importEmployees = createAsyncThunk(
  'employees/import',
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
      return rejectWithValue(error.response?.data?.detail || 'Import failed');
    }
  }
);

export const fetchEmployees = createAsyncThunk(
    'employees/fetchEmployees',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/employees');
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch employees');
        }
    }
);

const initialState = {
  list: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  importStatus: 'idle', // 'idle' | 'importing' | 'succeeded' | 'failed'
  importResult: null,
  error: null,
  employees: [],
};

const employeeSlice = createSlice({
  name: 'employees',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Bulk import reducers
      .addCase(importEmployees.pending, (state) => {
        state.importStatus = 'importing';
        state.importResult = null;
        state.error = null;
      })
      .addCase(importEmployees.fulfilled, (state, action) => {
        state.importStatus = 'succeeded';
        state.importResult = action.payload;
      })
      .addCase(importEmployees.rejected, (state, action) => {
        state.importStatus = 'failed';
        state.error = action.payload;
      })
      .addCase(fetchEmployees.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchEmployees.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = action.payload;
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  },
});

export default employeeSlice.reducer; 