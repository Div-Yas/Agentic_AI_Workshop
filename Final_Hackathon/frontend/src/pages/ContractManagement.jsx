import React from 'react';
import { useSelector } from 'react-redux';
import { Box, Typography } from '@mui/material';
import ContractUpload from '../components/contract/ContractUpload';
import ContractResult from '../components/contract/ContractResult';

const ContractManagement = () => {
  const { uploadStatus, parsedData } = useSelector((state) => state.contract);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        Contract Management
      </Typography>
      
      {uploadStatus.success && parsedData ? (
        <ContractResult />
      ) : (
        <ContractUpload />
      )}
    </Box>
  );
};

export default ContractManagement; 