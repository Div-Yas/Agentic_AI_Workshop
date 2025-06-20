import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Paper, Typography } from '@mui/material';

const columns = [
    { field: 'employee_id', headerName: 'Employee ID', flex: 1 },
    { field: 'name', headerName: 'Name', flex: 1.5 },
    { field: 'email', headerName: 'Email', flex: 2 },
    { field: 'designation', headerName: 'Designation', flex: 1.5 },
    { field: 'department', headerName: 'Department', flex: 1.5 },
    { field: 'status', headerName: 'Status', flex: 1 },
];

const EmployeeList = ({ employees }) => {
    return (
        <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
                Employee List
            </Typography>
            <DataGrid
                rows={employees.map(emp => ({ ...emp, id: emp._id }))}
                columns={columns}
                pageSize={10}
                rowsPerPageOptions={[10, 25, 50]}
                autoHeight
                sx={{ border: 0 }}
            />
        </Paper>
    );
};

export default EmployeeList; 