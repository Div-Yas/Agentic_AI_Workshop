import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box, Stepper, Step, StepLabel, StepContent, Typography, Paper, CircularProgress, Alert
} from '@mui/material';
import { fetchWorkflowStatus } from '../../store/slices/contractSlice';

const AGENT_ORDER = [
    'ContractReaderAgent',
    'SalaryCalculatorAgent',
    'ComplianceMapperAgent',
    'AnomalyDetectorAgent',
    'DocumentGeneratorAgent'
];

const WorkflowProgressTracker = () => {
  const dispatch = useDispatch();
  const { activeRequestId, workflowState, uploadStatus } = useSelector((state) => state.contract);

  useEffect(() => {
    let intervalId;

    if (activeRequestId && workflowState?.workflow_status !== 'COMPLETED' && workflowState?.workflow_status !== 'FAILED') {
      intervalId = setInterval(() => {
        dispatch(fetchWorkflowStatus(activeRequestId));
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [dispatch, activeRequestId, workflowState]);

  if (!activeRequestId) {
    if (uploadStatus.error) {
        return <Alert severity="error" sx={{ mt: 2 }}>Upload failed: {uploadStatus.error}</Alert>
    }
    return null; // Don't show anything if there's no active process
  }

  const agentProgress = workflowState?.agent_progress || {};
  const currentStatus = workflowState?.workflow_status || 'PENDING';

  const getStepIcon = (agentName) => {
    const status = agentProgress[agentName]?.status;
    if (status === 'RUNNING' || (currentStatus === 'RUNNING' && !status)) {
      return <CircularProgress size={24} />;
    }
    return null;
  };
  
  const isStepCompleted = (agentName) => {
    const status = agentProgress[agentName]?.status;
    return status === 'COMPLETED';
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Processing Payroll...
      </Typography>
      <Box sx={{ maxWidth: 400 }}>
        <Stepper activeStep={Object.keys(agentProgress).length -1} orientation="vertical">
          {AGENT_ORDER.map((agentName) => (
            <Step key={agentName} expanded={true}>
              <StepLabel
                StepIconComponent={() => getStepIcon(agentName)}
                completed={isStepCompleted(agentName)}
              >
                {agentName.replace('Agent', '')}
              </StepLabel>
              <StepContent>
                <Typography variant="caption">
                  {agentProgress[agentName]?.message || 'Waiting to start...'}
                </Typography>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Box>
      {currentStatus === 'COMPLETED' && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Workflow completed successfully!
        </Alert>
      )}
      {currentStatus === 'FAILED' && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Workflow failed: {workflowState?.error_message || 'An unknown error occurred.'}
        </Alert>
      )}
    </Paper>
  );
};

export default WorkflowProgressTracker; 