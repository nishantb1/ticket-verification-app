import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import CustomerForm from './pages/CustomerForm';
import AdminDashboard from './pages/AdminDashboard';
import Analytics from './pages/Analytics';
import CsvManagement from './pages/CsvManagement';
import Login from './pages/Login';
import ChangePassword from './pages/ChangePassword';
import { useAuth } from './hooks/useAuth';

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        Loading...
      </Box>
    );
  }

  return (
    <Router>
      <Layout>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<CustomerForm />} />
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes */}
          <Route
            path="/admin"
            element={
              isAuthenticated ? <AdminDashboard /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/analytics"
            element={
              isAuthenticated ? <Analytics /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/csv-management"
            element={
              isAuthenticated ? <CsvManagement /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/change-password"
            element={
              isAuthenticated ? <ChangePassword /> : <Navigate to="/login" />
            }
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App; 