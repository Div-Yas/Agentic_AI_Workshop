import React, { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useDropzone } from 'react-dropzone';
import {
  Box, Button, List, ListItem, ListItemText, IconButton, Typography, Paper,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { AddCircleOutline, Delete, CloudUpload } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

import { 
  addFilesToUpload, 
  removeFileFromUpload, 
  uploadContract,
  clearUploadState
} from '../../store/slices/contractSlice';
import { fetchDashboardSummary } from '../../store/slices/payrollSlice';
import { fetchEmployees } from '../../store/slices/employeeSlice';
import { contractUploadSchema } from '../../schemas/contractValidation';

const DropzoneContainer = styled(Paper)(({ theme, $isDragActive }) => ({
  border: `2px dashed ${$isDragActive ? theme.palette.primary.main : theme.palette.divider}`,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  backgroundColor: $isDragActive ? theme.palette.action.hover : theme.palette.background.paper,
  transition: 'background-color 0.3s',
  minHeight: '150px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
}));

const ContractUpload = () => {
  const dispatch = useDispatch();
  const { filesToUpload, uploadStatus } = useSelector((state) => state.contract);
  const [localFiles, setLocalFiles] = useState([]);

  const { handleSubmit, control, setValue, formState: { errors } } = useForm({
    resolver: yupResolver(contractUploadSchema),
    defaultValues: { files: [] },
  });

  const onDrop = useCallback((acceptedFiles) => {
    dispatch(clearUploadState()); // Clear previous state on new drop
    const uniqueNewFiles = acceptedFiles.filter(
      (file) => !localFiles.some((localFile) => localFile.name === file.name) &&
                 !filesToUpload.includes(file.name)
    );
    
    if (uniqueNewFiles.length > 0) {
      const updatedLocalFiles = [...localFiles, ...uniqueNewFiles];
      setLocalFiles(updatedLocalFiles);
      const fileNames = uniqueNewFiles.map(file => file.name);
      dispatch(addFilesToUpload(fileNames));
      setValue('files', updatedLocalFiles, { shouldValidate: true });
    }
  }, [dispatch, localFiles, filesToUpload, setValue]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    }
  });

  const handleRemoveFile = (fileName) => {
    dispatch(removeFileFromUpload(fileName));
    const updatedLocalFiles = localFiles.filter(file => file.name !== fileName);
    setLocalFiles(updatedLocalFiles);
    setValue('files', updatedLocalFiles, { shouldValidate: true });
  };

  const handleUpload = () => {
    const filesToUploadNow = localFiles.filter(localFile => filesToUpload.includes(localFile.name));
    filesToUploadNow.forEach(file => {
      dispatch(uploadContract(file)).then((result) => {
        if (result.meta.requestStatus === 'fulfilled') {
          // On successful upload, refresh dashboard and employee data
          dispatch(fetchDashboardSummary());
          dispatch(fetchEmployees());
        }
      });
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Upload Contracts</Typography>
      <form onSubmit={handleSubmit(handleUpload)}>
        <Controller
          name="files"
          control={control}
          render={() => (
            <DropzoneContainer {...getRootProps()} $isDragActive={isDragActive}>
              <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography>Drag & drop files here, or click to select files</Typography>
              <Typography variant="caption">PDF, DOCX, TXT up to 10MB</Typography>
            </DropzoneContainer>
          )}
        />
        {errors.files && (
          <Typography color="error" variant="body2" sx={{ mt: 1 }}>
            {errors.files.message || (errors.files.of && errors.files.of.message)}
          </Typography>
        )}

        {filesToUpload.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">Files to Upload:</Typography>
            <List>
              {filesToUpload.map((fileName) => (
                <ListItem
                  key={fileName}
                  secondaryAction={
                    <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveFile(fileName)}>
                      <Delete />
                    </IconButton>
                  }
                >
                  <ListItemText primary={fileName} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        <Button
          type="submit"
          variant="contained"
          color="primary"
          startIcon={<AddCircleOutline />}
          disabled={filesToUpload.length === 0 || uploadStatus.loading}
          sx={{ mt: 2 }}
        >
          {uploadStatus.loading ? 'Uploading...' : 'Upload & Process'}
        </Button>
      </form>
    </Box>
  );
};

export default ContractUpload; 