import React, { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Grid, Paper, Typography, Box, CircularProgress, Alert, Button } from '@mui/material';
import { fetchDashboardSummary, importEmployees } from '../../store/slices/payrollSlice';
import { fetchEmployees } from '../../store/slices/employeeSlice';
import EmployeeList from './EmployeeList';
import KpiCard from './KpiCard';
import { PeopleAlt, RequestPage, BugReport, CheckCircle, CloudUpload as CloudUploadIcon, Download as DownloadIcon } from '@mui/icons-material';

const PayrollDashboard = () => {
    const dispatch = useDispatch();
    const { summary, status, error, importStatus, importError } = useSelector((state) => state.payroll);
    const { list: employees, status: employeeStatus } = useSelector((state) => state.employees);
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (status === 'idle') {
            dispatch(fetchDashboardSummary());
        }
        if (employeeStatus === 'idle') {
            dispatch(fetchEmployees());
        }
    }, [status, employeeStatus, dispatch]);

    useEffect(() => {
     dispatch(fetchEmployees());
     dispatch(fetchDashboardSummary());
    }, []);

    const handleImportClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            dispatch(importEmployees(file)).then((result) => {
                if (result.meta.requestStatus === 'fulfilled') {
                    // Refresh employee list and dashboard summary after successful import
                    dispatch(fetchEmployees());
                    dispatch(fetchDashboardSummary());
                }
            });
        }
    };

    const handleDownloadSample = () => {
        const link = document.createElement('a');
        link.href = '/sample_employees.xlsx';
        link.setAttribute('download', 'sample_employees.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    if (status === 'loading' || employeeStatus === 'loading') {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return <Alert severity="error">Error loading dashboard: {error}</Alert>;
    }

    const kpiData = summary?.kpis ?? {};

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>Payroll Dashboard</Typography>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="h6" gutterBottom>Quick Actions</Typography>
                        <Box>
                            <input
                                type="file"
                                ref={fileInputRef}
                                style={{ display: 'none' }}
                                onChange={handleFileChange}
                                accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                            />
                            <Button
                                variant="contained"
                                color="primary"
                                startIcon={<CloudUploadIcon />}
                                onClick={handleImportClick}
                                disabled={importStatus === 'loading'}
                                sx={{ mr: 1 }}
                            >
                                Import Employees
                            </Button>
                            <Button
                                variant="outlined"
                                color="secondary"
                                startIcon={<DownloadIcon />}
                                onClick={handleDownloadSample}
                            >
                                Download Sample
                            </Button>
                        </Box>
                        {importStatus === 'loading' && <CircularProgress size={24} sx={{ ml: 2, mt: 1 }} />}
                        {importStatus === 'succeeded' && <Alert severity="success" sx={{ mt: 2 }}>File imported successfully!</Alert>}
                        {importError && <Alert severity="error" sx={{ mt: 2 }}>{`Import failed: ${importError}`}</Alert>}
                    </Paper>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <KpiCard title="Total Employees" value={kpiData.total_employees ?? 0} icon={<PeopleAlt />} />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <KpiCard title="Payroll Accuracy" value={`${kpiData.payroll_accuracy ?? 100}%`} icon={<CheckCircle />} />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <KpiCard title="Compliance Status" value={`${kpiData.compliance_status ?? 100}%`} icon={<RequestPage />} />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <KpiCard title="Total Disbursed" value={`$${kpiData.total_disbursed ?? 0}`} icon={<BugReport />} />
                </Grid>

                {/* Employee List */}
                
            </Grid>
            <Box sx={{ mt: 4 }}>
                <EmployeeList employees={employees} />
            </Box>
            
        </Container>
    );
};

export default PayrollDashboard; 