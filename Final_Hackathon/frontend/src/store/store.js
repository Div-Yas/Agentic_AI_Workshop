import { configureStore } from '@reduxjs/toolkit';
import payrollReducer from './slices/payrollSlice';
import employeeReducer from './slices/employeeSlice';
import contractReducer from './slices/contractSlice';
import complianceReducer from './slices/complianceSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    payroll: payrollReducer,
    employees: employeeReducer,
    contract: contractReducer,
    compliance: complianceReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types, useful for file uploads
        ignoredActions: ['contract/uploadContract/pending'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.file'],
        // Ignore these paths in the state
        ignoredPaths: ['contract.file'],
      },
    }),
}); 