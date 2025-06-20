import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
} from '@mui/material';
import { CheckCircle, Download, ExpandMore } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { clearUploadState } from '../../store/slices/contractSlice';

const DataDisplayer = ({ data }) => {
    const renderData = (obj) => {
      const preferredOrder = ['employee_id', 'employee_name'];
      const allKeys = Object.keys(obj);
      const sortedKeys = [
        ...preferredOrder.filter(k => allKeys.includes(k)),
        ...allKeys.filter(k => !preferredOrder.includes(k))
      ];
  
      return sortedKeys.map((key) => {
        const value = obj[key];
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
        if (Array.isArray(value)) {
          return (
            <Box key={key} sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">{formattedKey}:</Typography>
              <Box sx={{ pl: 2 }}>
                {value.map((item, i) => (
                  <Typography key={i} variant="body2" sx={{ fontFamily: 'monospace' }}>
                    • {item}
                  </Typography>
                ))}
              </Box>
            </Box>
          );
        }
  
        if (typeof value === 'object' && value !== null) {
          return (
            <Box key={key} sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">{formattedKey}:</Typography>
              <Box sx={{ pl: 2, borderLeft: '3px solid #eee', ml: 1 }}>
                {renderData(value)}
              </Box>
            </Box>
          );
        }
  
        return (
          <Box key={key} sx={{ mb: 1 }}>
            <Typography variant="body2">
              <strong>{formattedKey}:</strong>{' '}
              <Box component="span" sx={{ fontFamily: 'monospace' }}>{String(value)}</Box>
            </Typography>
          </Box>
        );
      });
    };
  
    return <Box>{renderData(data)}</Box>;
};
  

const ContractResult = () => {
    const dispatch = useDispatch();
    const { parsedData, filesToUpload } = useSelector((state) => state.contract);
    
    if (!parsedData) {
        return null;
    }

    const { contract_data, payslip_url } = parsedData;
    const fileName = filesToUpload.length > 0 ? filesToUpload[0] : 'contract.docx';

    const handleDownload = () => {
        if (payslip_url) {
            window.open(`http://localhost:8000${payslip_url}`, '_blank');
        }
    };

    const handleProcessAnother = () => {
        dispatch(clearUploadState());
    };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Upload Status
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="body1">{fileName}</Typography>
        <Box>
            <Chip
                icon={<CheckCircle />}
                label="Success"
                color="success"
                sx={{ mr: 1 }}
            />
            <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleDownload}
                disabled={!payslip_url}
            >
                Payslip
            </Button>
        </Box>
      </Box>

      <Accordion defaultExpanded>
        <AccordionSummary
          expandIcon={<ExpandMore />}
        >
          <Typography>View Parsed Data</Typography>
        </AccordionSummary>
        <AccordionDetails>
            <DataDisplayer data={contract_data} />
        </AccordionDetails>
      </Accordion>
      <Button variant="contained" onClick={handleProcessAnother} sx={{ mt: 2 }}>
        Process Another Contract
      </Button>
    </Paper>
  );
};

export default ContractResult; 