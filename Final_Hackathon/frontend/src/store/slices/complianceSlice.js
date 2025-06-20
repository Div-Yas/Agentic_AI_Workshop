import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // This state seems to be part of payroll.
  // Re-checking the provided schema.
  // The schema is:
  // payroll: { complianceData: {} }
  // So this slice might not be needed, or it should handle more specific compliance state.
  // For now, I'll create it as requested but it may be merged into payrollSlice later.
  complianceRules: [],
  validationStatus: 'idle',
  error: null,
};

const complianceSlice = createSlice({
  name: 'compliance',
  initialState,
  reducers: {},
  extraReducers: (builder) => {}
});

export default complianceSlice.reducer; 