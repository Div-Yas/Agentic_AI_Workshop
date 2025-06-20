import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/common/Layout';
import ContractManagement from './pages/ContractManagement';
import ContractPreview from './components/contract/ContractPreview';
import PayrollDashboard from './components/dashboard/PayrollDashboard';


const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<PayrollDashboard />} />
        <Route path="/contracts" element={<ContractManagement />} />
        <Route path="/contracts/:id" element={<ContractPreview />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes; 