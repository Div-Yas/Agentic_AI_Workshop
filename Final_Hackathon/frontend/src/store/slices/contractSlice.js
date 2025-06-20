import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const uploadContract = createAsyncThunk(
    'contract/uploadContract',
    async (file, { rejectWithValue }) => {
        try {
            const formData = new FormData();
            formData.append('file', file);
            const response = await api.post('/payroll/upload-and-process', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.detail || 'Contract upload failed');
        }
    }
);

const initialState = {
    filesToUpload: [], // Store file names
    uploadStatus: { loading: false, error: null, success: false },
    parsedData: null,
};

const contractSlice = createSlice({
    name: 'contract',
    initialState,
    reducers: {
        addFilesToUpload: (state, action) => {
            state.filesToUpload = [...new Set([...state.filesToUpload, ...action.payload])];
        },
        removeFileFromUpload: (state, action) => {
            state.filesToUpload = state.filesToUpload.filter(name => name !== action.payload);
        },
        clearUploadState: (state) => {
            state.filesToUpload = [];
            state.uploadStatus = { loading: false, error: null, success: false };
            state.parsedData = null;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(uploadContract.pending, (state) => {
                state.uploadStatus.loading = true;
                state.uploadStatus.error = null;
                state.uploadStatus.success = false;
            })
            .addCase(uploadContract.fulfilled, (state, action) => {
                state.uploadStatus.loading = false;
                state.uploadStatus.success = true;
                state.parsedData = action.payload;
            })
            .addCase(uploadContract.rejected, (state, action) => {
                state.uploadStatus.loading = false;
                state.uploadStatus.error = action.payload;
            });
    }
});

export const { addFilesToUpload, removeFileFromUpload, clearUploadState } = contractSlice.actions;
export default contractSlice.reducer; 