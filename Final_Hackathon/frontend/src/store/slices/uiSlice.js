import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  activeStep: 0,
  selectedEmployee: null,
  filters: {},
  notifications: []
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setActiveStep: (state, action) => {
      state.activeStep = action.payload;
    },
    showNotification: (state, action) => {
        state.notifications.push(action.payload);
    },
    hideNotification: (state, action) => {
        state.notifications = state.notifications.filter(
            (notification) => notification.id !== action.payload
        );
    }
  }
});

export const { setActiveStep, showNotification, hideNotification } = uiSlice.actions;
export default uiSlice.reducer; 