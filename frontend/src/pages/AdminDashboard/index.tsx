import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  Visibility as ViewIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiService from '../../services/api';
import { Wave, Order, CsvUpload, Analytics } from '../../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AdminDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(() => {
    const savedTab = localStorage.getItem('adminDashboardTab');
    return savedTab ? parseInt(savedTab) : 0;
  });
  const [waveDialogOpen, setWaveDialogOpen] = useState(false);
  const [editingWave, setEditingWave] = useState<Wave | null>(null);
  const [waveForm, setWaveForm] = useState({
    name: '',
    start_date: '',
    end_date: '',
    boys_price: 14,
    girls_price: 14,
    is_active: true,
  });
  const [deleteOrderDialogOpen, setDeleteOrderDialogOpen] = useState(false);
  const [orderToDelete, setOrderToDelete] = useState<Order | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);

  const queryClient = useQueryClient();

  // Save tab value to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('adminDashboardTab', tabValue.toString());
  }, [tabValue]);

  // Queries
  const { data: waves = [], isLoading: wavesLoading } = useQuery<Wave[]>({
    queryKey: ['waves'],
    queryFn: apiService.getWaves,
  });

  const { data: ordersResponse, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => apiService.getOrders(),
  });

  const { data: analytics } = useQuery<Analytics>({
    queryKey: ['analytics'],
    queryFn: () => apiService.getAnalytics(),
    staleTime: 0, // Always consider data stale
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  });

  const { data: csvUploads = [], isLoading: csvUploadsLoading } = useQuery<CsvUpload[]>({
    queryKey: ['csvUploads'],
    queryFn: () => apiService.getCsvUploads(),
    staleTime: 0, // Always consider data stale
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  });

  // Extract orders from paginated response
  const orders = ordersResponse?.data || [];

  // Mutations
  const createWaveMutation = useMutation({
    mutationFn: (data: any) => apiService.createWave(data),
    onSuccess: (response) => {
      console.log('Wave created successfully:', response);
      queryClient.refetchQueries({ queryKey: ['waves'] });
      queryClient.refetchQueries({ queryKey: ['currentWave'] });
      queryClient.invalidateQueries({ queryKey: ['currentWave'] });
      setWaveDialogOpen(false);
      setWaveForm({ name: '', start_date: '', end_date: '', boys_price: 14, girls_price: 14, is_active: true });
      alert('Wave created successfully!');
    },
    onError: (error) => {
      console.error('Error creating wave:', error);
      alert('Error creating wave. Please try again.');
    },
  });

  const updateWaveMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => apiService.updateWave(id, data),
    onSuccess: (response) => {
      console.log('Wave updated successfully:', response);
      queryClient.refetchQueries({ queryKey: ['waves'] });
      queryClient.refetchQueries({ queryKey: ['currentWave'] });
      queryClient.invalidateQueries({ queryKey: ['currentWave'] });
      setWaveDialogOpen(false);
      setEditingWave(null);
      setWaveForm({ name: '', start_date: '', end_date: '', boys_price: 14, girls_price: 14, is_active: true });
      alert('Wave updated successfully!');
    },
    onError: (error) => {
      console.error('Error updating wave:', error);
      alert('Error updating wave. Please try again.');
    },
  });

  const deleteWaveMutation = useMutation({
    mutationFn: apiService.deleteWave,
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: ['waves'] });
      queryClient.refetchQueries({ queryKey: ['currentWave'] });
      queryClient.invalidateQueries({ queryKey: ['currentWave'] });
      alert('Wave deleted successfully!');
    },
    onError: (error) => {
      console.error('Error deleting wave:', error);
      alert('Error deleting wave. Please try again.');
    },
  });

  const deleteOrderMutation = useMutation({
    mutationFn: apiService.deleteOrder,
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: ['orders'] });
      setDeleteOrderDialogOpen(false);
      setOrderToDelete(null);
      alert('Order deleted successfully!');
    },
    onError: (error: any) => {
      console.error('Error deleting order:', error);
      alert(`Error deleting order: ${error.response?.data?.message || error.message || 'Unknown error'}`);
    },
  });

  const csvUploadMutation = useMutation({
    mutationFn: (file: File) => apiService.uploadCsv(file),
    onSuccess: (response) => {
      console.log('CSV uploaded successfully:', response);
      console.log('Invalidating analytics cache...');
      // Force immediate refetch of all related data
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      queryClient.invalidateQueries({ queryKey: ['csvUploads'] });
      console.log('Refetching analytics...');
      queryClient.refetchQueries({ queryKey: ['analytics'] });
      queryClient.refetchQueries({ queryKey: ['csvUploads'] });
      setCsvFile(null);
      alert('CSV uploaded successfully!');
    },
    onError: (error) => {
      console.error('Error uploading CSV:', error);
      alert('Error uploading CSV. Please try again.');
    },
  });

  // Auto-set end date when start date changes
  useEffect(() => {
    if (waveForm.start_date) {
      const startDate = new Date(waveForm.start_date);
      const endDate = new Date(startDate);
      endDate.setDate(endDate.getDate() + 3);
      setWaveForm(prev => ({
        ...prev,
        end_date: endDate.toISOString().split('T')[0],
      }));
    }
  }, [waveForm.start_date]);

  // Set default dates when opening dialog
  useEffect(() => {
    if (waveDialogOpen && !editingWave) {
      const today = new Date().toISOString().split('T')[0];
      const threeDaysLater = new Date();
      threeDaysLater.setDate(threeDaysLater.getDate() + 3);
      setWaveForm({
        name: '',
        start_date: today,
        end_date: threeDaysLater.toISOString().split('T')[0],
        boys_price: 14,
        girls_price: 14,
        is_active: true,
      });
    }
  }, [waveDialogOpen, editingWave]);

  // Debug analytics data changes
  useEffect(() => {
    if (analytics) {
      console.log('Analytics data updated:', analytics);
      console.log('Venmo transactions:', analytics.venmo_transactions);
      console.log('Zelle transactions:', analytics.zelle_transactions);
    }
  }, [analytics]);

  // Debug CSV uploads data changes
  useEffect(() => {
    if (csvUploads) {
      console.log('CSV uploads data updated:', csvUploads);
      console.log('Number of uploads:', csvUploads.length);
    }
  }, [csvUploads]);

  const handleWaveSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('handleWaveSubmit called');
    console.log('editingWave:', editingWave);
    console.log('waveForm:', waveForm);
    console.log('waveForm JSON:', JSON.stringify(waveForm, null, 2));
    
    if (editingWave) {
      console.log('Updating wave with id:', editingWave.id);
      console.log('Sending data:', { id: editingWave.id, data: waveForm });
      updateWaveMutation.mutate({ id: editingWave.id, data: waveForm });
    } else {
      console.log('Creating new wave');
      console.log('Sending data:', waveForm);
      createWaveMutation.mutate(waveForm);
    }
  };

  const handleEditWave = (wave: Wave) => {
    console.log('handleEditWave called with wave:', wave);
    setEditingWave(wave);
    setWaveForm({
      name: wave.name,
      start_date: wave.start_date,
      end_date: wave.end_date,
      boys_price: wave.boys_price,
      girls_price: wave.girls_price,
      is_active: wave.is_active,
    });
    console.log('Wave form set to:', {
      name: wave.name,
      start_date: wave.start_date,
      end_date: wave.end_date,
      boys_price: wave.boys_price,
      girls_price: wave.girls_price,
      is_active: wave.is_active,
    });
    setWaveDialogOpen(true);
  };

  const handleDeleteWave = (id: number) => {
    console.log('handleDeleteWave called with id:', id);
    if (window.confirm('Are you sure you want to delete this wave?')) {
      console.log('User confirmed deletion, calling deleteWaveMutation.mutate');
      deleteWaveMutation.mutate(id);
    }
  };

  const handleDeleteOrder = (order: Order) => {
    setOrderToDelete(order);
    setDeleteOrderDialogOpen(true);
  };

  const handleViewReceipt = (order: Order) => {
    if (order.receipt_path) {
      const receiptUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/receipts/${order.receipt_path}`;
      window.open(receiptUrl, '_blank');
    } else {
      alert('No receipt available for this order.');
    }
  };

  const handleExportVerifiedEmails = async () => {
    try {
      const result = await apiService.getVerifiedEmails();
      
      if (result.count === 0) {
        alert('No verified emails found.');
        return;
      }
      
      // Copy to clipboard
      await navigator.clipboard.writeText(result.email_list);
      alert(`Copied ${result.count} verified emails to clipboard!\n\nYou can now paste them into Ticketbud.`);
      
      // Also show the emails in a dialog for reference
      const emailDialog = window.open('', '_blank');
      if (emailDialog) {
        emailDialog.document.write(`
          <html>
            <head><title>Verified Emails for Ticketbud</title></head>
            <body>
              <h2>Verified Emails (${result.count} total)</h2>
              <p>These emails have been copied to your clipboard and can be pasted into Ticketbud:</p>
              <textarea style="width: 100%; height: 400px; font-family: monospace;">${result.email_list}</textarea>
              <br><br>
              <p><strong>Order Details:</strong></p>
              <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr><th>Email</th><th>Name</th><th>Amount</th><th>Date</th></tr>
                ${result.orders.map(order => `
                  <tr>
                    <td>${order.email}</td>
                    <td>${order.name}</td>
                    <td>$${order.amount}</td>
                    <td>${new Date(order.created_at).toLocaleDateString()}</td>
                  </tr>
                `).join('')}
              </table>
            </body>
          </html>
        `);
      }
    } catch (error) {
      console.error('Error exporting verified emails:', error);
      alert('Error exporting verified emails. Please try again.');
    }
  };

  const confirmDeleteOrder = () => {
    if (orderToDelete) {
      deleteOrderMutation.mutate(orderToDelete.id);
    }
  };

  const handleCsvUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvFile) {
      alert('Please select a CSV file to upload.');
      return;
    }
    csvUploadMutation.mutate(csvFile);
  };

  const pendingOrders = orders.filter((order: Order) => order.status === 'Pending');
  const approvedOrders = orders.filter((order: Order) => order.status === 'Approved');
  const rejectedOrders = orders.filter((order: Order) => order.status === 'Rejected');

  const handleToggleWaveStatus = async (wave: Wave) => {
    const newStatus = !wave.is_active;
    
    try {
      if (newStatus) {
        // If activating this wave, deactivate all others first
        for (const otherWave of waves) {
          if (otherWave.id !== wave.id && otherWave.is_active) {
            await apiService.updateWave(otherWave.id, { is_active: false });
          }
        }
      }
      
      // Update the target wave
      await apiService.updateWave(wave.id, { is_active: newStatus });
      
      // Refetch waves to get updated data
      queryClient.refetchQueries({ queryKey: ['waves'] });
      queryClient.refetchQueries({ queryKey: ['currentWave'] });
      
      // Also invalidate the currentWave query to force a fresh fetch
      queryClient.invalidateQueries({ queryKey: ['currentWave'] });
      
      alert(`Wave "${wave.name}" ${newStatus ? 'activated' : 'deactivated'} successfully!`);
    } catch (error) {
      console.error('Error toggling wave status:', error);
      alert(`Error toggling wave status for "${wave.name}". Please try again.`);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Dashboard
      </Typography>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Pending Orders
              </Typography>
              <Typography variant="h3" color="warning.main">
                {pendingOrders.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Approved Orders
              </Typography>
              <Typography variant="h3" color="success.main">
                {approvedOrders.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Waves
              </Typography>
              <Typography variant="h3" color="primary.main">
                {waves.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Orders
              </Typography>
              <Typography variant="h3" color="info.main">
                {orders.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Orders" />
          <Tab label="Wave Management" />
          <Tab label="CSV Management" />
          <Tab label="Analytics" />
        </Tabs>

        {/* Orders Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Orders
            </Typography>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={() => queryClient.invalidateQueries({ queryKey: ['orders'] })}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExportVerifiedEmails}
              sx={{ ml: 1 }}
            >
              Export Verified Emails
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Tickets</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.slice(0, 10).map((order: Order) => (
                  <TableRow key={order.id}>
                    <TableCell>{order.name}</TableCell>
                    <TableCell>{order.email}</TableCell>
                    <TableCell>
                      {order.boys_count} Boys, {order.girls_count} Girls
                    </TableCell>
                    <TableCell>${order.expected_amount}</TableCell>
                    <TableCell>
                      <Chip
                        label={order.status}
                        color={
                          order.status === 'Verified'
                            ? 'success'
                            : order.status === 'Approved'
                            ? 'success'
                            : order.status === 'Rejected'
                            ? 'error'
                            : 'warning'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(order.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleViewReceipt(order)}>
                        <ViewIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleDeleteOrder(order)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Wave Management Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Wave Management
          </Typography>
          
          {/* Current Active Wave Display */}
          {waves.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Current Active Wave:
              </Typography>
              {waves.find(w => w.is_active) ? (
                <Card sx={{ bgcolor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
                  <CardContent>
                    <Typography variant="h6" color="success.main">
                      {waves.find(w => w.is_active)?.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {waves.find(w => w.is_active)?.start_date} - {waves.find(w => w.is_active)?.end_date}
                    </Typography>
                    <Typography variant="body2">
                      Boys: ${waves.find(w => w.is_active)?.boys_price} | Girls: ${waves.find(w => w.is_active)?.girls_price}
                    </Typography>
                  </CardContent>
                </Card>
              ) : (
                <Alert severity="warning">
                  No active wave found. Please activate a wave to set current prices.
                </Alert>
              )}
            </Box>
          )}

          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">All Waves</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setWaveDialogOpen(true)}
            >
              Add New Wave
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Start Date</TableCell>
                  <TableCell>End Date</TableCell>
                  <TableCell>Boys Price</TableCell>
                  <TableCell>Girls Price</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {waves.map((wave: Wave) => (
                  <TableRow key={wave.id}>
                    <TableCell>{wave.name}</TableCell>
                    <TableCell>{wave.start_date}</TableCell>
                    <TableCell>{wave.end_date}</TableCell>
                    <TableCell>${wave.boys_price}</TableCell>
                    <TableCell>${wave.girls_price}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={wave.is_active ? 'Active' : 'Inactive'}
                          color={wave.is_active ? 'success' : 'default'}
                          size="small"
                        />
                        <IconButton
                          size="small"
                          onClick={() => handleToggleWaveStatus(wave)}
                          title={wave.is_active ? 'Deactivate Wave' : 'Activate Wave'}
                          color={wave.is_active ? 'error' : 'success'}
                        >
                          {wave.is_active ? <BlockIcon /> : <CheckCircleIcon />}
                        </IconButton>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleEditWave(wave)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteWave(wave.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* CSV Management Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            CSV Management
          </Typography>
          
          <Grid container spacing={3}>
            {/* Upload Section */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Upload Transaction CSV
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Upload Chase, Venmo, or Zelle CSV files to cross-check with receipts
                  </Typography>
                  
                  <Box component="form" onSubmit={handleCsvUpload} sx={{ mt: 2 }}>
                    <input
                      accept=".csv"
                      style={{ display: 'none' }}
                      id="csv-file-input"
                      type="file"
                      onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                    />
                    <label htmlFor="csv-file-input">
                      <Button
                        variant="outlined"
                        component="span"
                        startIcon={<UploadIcon />}
                        sx={{ mb: 2 }}
                      >
                        Select CSV File
                      </Button>
                    </label>
                    
                    {csvFile && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          Selected: {csvFile.name}
                        </Typography>
                      </Box>
                    )}
                    
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={!csvFile || csvUploadMutation.isPending}
                      startIcon={<UploadIcon />}
                    >
                      {csvUploadMutation.isPending ? 'Uploading...' : 'Upload CSV'}
                    </Button>
                  </Box>
                  
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>Supported Formats:</strong>
                    </Typography>
                    <Typography variant="body2">
                      • <strong>Chase CSV:</strong> Details, Posting Date, Description, Amount, Type, Balance
                    </Typography>
                    <Typography variant="body2">
                      • <strong>Venmo CSV:</strong> Datetime, Type, Note, From, To, Amount, Fee, Net
                    </Typography>
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Stats Section */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Transaction Statistics
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary.main">
                          {analytics?.venmo_transactions || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Venmo Transactions
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          {analytics?.zelle_transactions || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Zelle Transactions
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={() => queryClient.invalidateQueries({ queryKey: ['analytics'] })}
                    sx={{ mt: 2 }}
                  >
                    Refresh Stats
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          {/* CSV Upload History */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload History
              </Typography>
              
              {csvUploadsLoading ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : csvUploads && csvUploads.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Upload Date</TableCell>
                        <TableCell>Filename</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Records</TableCell>
                        <TableCell>New</TableCell>
                        <TableCell>Updated</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {csvUploads.map((upload) => (
                        <TableRow key={upload.id}>
                          <TableCell>
                            {new Date(upload.upload_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>{upload.original_filename}</TableCell>
                          <TableCell>
                            <Chip
                              label={upload.upload_type}
                              color={upload.upload_type === 'venmo' ? 'primary' : 'success'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{upload.records_processed}</TableCell>
                          <TableCell>
                            <Chip label={upload.new_records} color="success" size="small" />
                          </TableCell>
                          <TableCell>
                            <Chip label={upload.updated_records} color="info" size="small" />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={upload.status}
                              color={upload.status === 'success' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
                  No CSV uploads yet. Upload your first CSV file to see history here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </TabPanel>

        {/* Analytics Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Analytics Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Analytics functionality coming soon...
          </Typography>
        </TabPanel>
      </Paper>

      {/* Wave Dialog */}
      <Dialog open={waveDialogOpen} onClose={() => setWaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingWave ? 'Edit Wave' : 'Add New Wave'}
        </DialogTitle>
        <form onSubmit={handleWaveSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Wave Name"
                  value={waveForm.name}
                  onChange={(e) => setWaveForm(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  value={waveForm.start_date}
                  onChange={(e) => setWaveForm(prev => ({ ...prev, start_date: e.target.value }))}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="End Date"
                  type="date"
                  value={waveForm.end_date}
                  onChange={(e) => setWaveForm(prev => ({ ...prev, end_date: e.target.value }))}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Boys Price"
                  type="number"
                  value={waveForm.boys_price}
                  onChange={(e) => setWaveForm(prev => ({ ...prev, boys_price: parseFloat(e.target.value) || 0 }))}
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Girls Price"
                  type="number"
                  value={waveForm.girls_price}
                  onChange={(e) => setWaveForm(prev => ({ ...prev, girls_price: parseFloat(e.target.value) || 0 }))}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={waveForm.is_active}
                    onChange={(e) => setWaveForm(prev => ({ ...prev, is_active: e.target.checked }))}
                  />
                  <label htmlFor="is_active">Active Wave</label>
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setWaveDialogOpen(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createWaveMutation.isPending || updateWaveMutation.isPending}
            >
              {createWaveMutation.isPending || updateWaveMutation.isPending ? (
                <CircularProgress size={20} />
              ) : editingWave ? (
                'Update Wave'
              ) : (
                'Add Wave'
              )}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Delete Order Confirmation Dialog */}
      <Dialog open={deleteOrderDialogOpen} onClose={() => setDeleteOrderDialogOpen(false)}>
        <DialogTitle>Delete Order</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the order for <strong>{orderToDelete?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOrderDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmDeleteOrder}
            color="error"
            variant="contained"
            disabled={deleteOrderMutation.isPending}
          >
            {deleteOrderMutation.isPending ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminDashboard; 