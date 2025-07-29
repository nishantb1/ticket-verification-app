import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  IconButton,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { useForm, Controller } from 'react-hook-form';
import { useMutation, useQuery } from '@tanstack/react-query';
import { CloudUpload, Receipt, Refresh } from '@mui/icons-material';
import apiService from '../../services/api';
import { OrderFormData } from '../../types';
import { useQueryClient } from '@tanstack/react-query';
import { Wave } from '../../types'; // Added missing import

const CustomerForm: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);

  const queryClient = useQueryClient();

  // Get current wave for pricing
  const { data: currentWave, isLoading: waveLoading, refetch: refetchWave, error: waveError } = useQuery<Wave | null>({
    queryKey: ['currentWave'],
    queryFn: apiService.getCurrentWave,
    refetchInterval: 5000, // Refetch every 5 seconds to catch wave status changes
    refetchIntervalInBackground: true,
    staleTime: 0, // Always consider data stale
    gcTime: 0, // Don't cache (updated from cacheTime)
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  });

  // Debug logging for React Query
  console.log('CustomerForm React Query Debug:', {
    currentWave,
    waveLoading,
    waveError,
    queryKey: ['currentWave']
  });

  // Load saved form data from localStorage
  const getSavedFormData = (): Partial<OrderFormData> => {
    try {
      const saved = localStorage.getItem('customerFormData');
      return saved ? JSON.parse(saved) : {};
    } catch (error) {
      console.error('Error loading saved form data:', error);
      return {};
    }
  };

  // Save form data to localStorage
  const saveFormData = (data: Partial<OrderFormData>) => {
    try {
      localStorage.setItem('customerFormData', JSON.stringify(data));
    } catch (error) {
      console.error('Error saving form data:', error);
    }
  };

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
    setValue,
  } = useForm<OrderFormData>({
    defaultValues: {
      name: '',
      email: '',
      boys_tickets: 0,
      girls_tickets: 0,
      receipt: null,
      ...getSavedFormData(),
    },
  });

  // Watch form values for persistence
  const watchedValues = watch();
  
  // Save form data whenever values change
  useEffect(() => {
    const { receipt, ...dataToSave } = watchedValues;
    saveFormData(dataToSave);
  }, [watchedValues]);

  // Load saved data on component mount
  useEffect(() => {
    const savedData = getSavedFormData();
    if (savedData.name) setValue('name', savedData.name);
    if (savedData.email) setValue('email', savedData.email);
    if (savedData.boys_tickets) setValue('boys_tickets', savedData.boys_tickets);
    if (savedData.girls_tickets) setValue('girls_tickets', savedData.girls_tickets);
  }, [setValue]);

  const boysTickets = watch('boys_tickets');
  const girlsTickets = watch('girls_tickets');

  // Calculate total using wave prices or default to $14
  const boysPrice = currentWave?.boys_price || 14;
  const girlsPrice = currentWave?.girls_price || 14;
  const totalAmount = (boysTickets * boysPrice) + (girlsTickets * girlsPrice);

  // Debug logging
  console.log('CustomerForm Debug:', {
    currentWave,
    boysPrice,
    girlsPrice,
    boysTickets,
    girlsTickets,
    totalAmount
  });

  // Manual cache clear function
  const clearCacheAndRefetch = () => {
    console.log('Clearing cache and refetching...');
    // Clear React Query cache for currentWave
    queryClient.removeQueries({ queryKey: ['currentWave'] });
    // Force a fresh fetch
    refetchWave();
  };

  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = () => {
        setUploadPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  const createOrderMutation = useMutation({
    mutationFn: (data: OrderFormData) => {
      console.log('Creating order with data:', data);
      console.log('Current wave for pricing:', currentWave);
      console.log('Using prices - Boys:', boysPrice, 'Girls:', girlsPrice);
      
      const formData = {
        ...data,
        receipt: uploadedFile,
      };
      console.log('Sending form data:', formData);
      return apiService.createOrder(formData);
    },
    onSuccess: (response) => {
      console.log('Order created successfully:', response);
      if (response.success) {
        reset();
        setUploadedFile(null);
        setUploadPreview(null);
        // Clear saved form data
        localStorage.removeItem('customerFormData');
        // Refresh wave data to show any updates
        refetchWave();
      }
    },
    onError: (error) => {
      console.error('Error creating order:', error);
      alert(`Order submission failed: ${error.message || 'Unknown error'}`);
    },
  });

  const onSubmit = (data: OrderFormData) => {
    if (!uploadedFile) {
      return;
    }
    createOrderMutation.mutate(data);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
            Submit Your Order
          </Typography>

          {/* Current Wave Information */}
          {waveLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : waveError ? (
            <Alert severity="error" sx={{ mb: 3 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Error Loading Wave Data</strong>
              </Typography>
              <Typography variant="body2">
                Error: {waveError.message}
              </Typography>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => refetchWave()}
                sx={{ mt: 1 }}
              >
                Retry
              </Button>
            </Alert>
          ) : currentWave ? (
            <Paper sx={{ p: 3, mb: 3, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box>
                  <Typography variant="h6" gutterBottom color="primary.main" fontWeight="bold">
                    🎫 Current Wave: {currentWave.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(currentWave.start_date).toLocaleDateString()} - {new Date(currentWave.end_date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Debug: Wave ID {currentWave.id}, Active: {currentWave.is_active ? 'Yes' : 'No'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton 
                    onClick={() => refetchWave()} 
                    size="small" 
                    color="primary" 
                    aria-label="refresh wave"
                    title="Refresh wave data"
                  >
                    <Refresh />
                  </IconButton>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      console.log('Manual refresh clicked');
                      clearCacheAndRefetch();
                    }}
                  >
                    Force Refresh
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="secondary"
                    onClick={async () => {
                      console.log('Testing API call...');
                      try {
                        const response = await apiService.getCurrentWave();
                        console.log('API Response:', response);
                        alert(`API Response: ${JSON.stringify(response, null, 2)}`);
                      } catch (error) {
                        console.error('API Error:', error);
                        alert(`API Error: ${error}`);
                      }
                    }}
                  >
                    Test API
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="warning"
                    onClick={async () => {
                      console.log('Testing direct fetch...');
                      try {
                        const response = await fetch('http://localhost:5000/api/waves/current');
                        const data = await response.json();
                        console.log('Direct fetch response:', data);
                        alert(`Direct fetch: ${JSON.stringify(data, null, 2)}`);
                      } catch (error) {
                        console.error('Direct fetch error:', error);
                        alert(`Direct fetch error: ${error}`);
                      }
                    }}
                  >
                    Test Fetch
                  </Button>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Boys' Tickets</Typography>
                  <Typography variant="h6" color="primary.main" fontWeight="bold">
                    ${boysPrice}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Girls' Tickets</Typography>
                  <Typography variant="h6" color="primary.main" fontWeight="bold">
                    ${girlsPrice}
                  </Typography>
                </Box>
              </Box>
              
              {/* Debug Information */}
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Debug Info: Using prices from wave "{currentWave.name}" (ID: {currentWave.id})
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary">
                  Boys: ${boysPrice}, Girls: ${girlsPrice} | Total: ${totalAmount}
                </Typography>
              </Box>
            </Paper>
          ) : (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body1" gutterBottom>
                <strong>No Active Wave Found</strong>
              </Typography>
              <Typography variant="body2">
                There is currently no active wave for ticket sales. Please check back later or contact an administrator to activate a wave.
              </Typography>
            </Alert>
          )}

          {createOrderMutation.isSuccess && (
            <Alert severity="success" sx={{ mb: 3 }}>
              Order submitted successfully! Your order ID is: {createOrderMutation.data?.data?.id}
            </Alert>
          )}

          {createOrderMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Error submitting order. Please try again.
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              {/* Personal Information */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Personal Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: 'Name is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Full Name"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="email"
                  control={control}
                  rules={{
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Email"
                      type="email"
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
                  )}
                />
              </Grid>



              {/* Ticket Selection */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Ticket Selection
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="boys_tickets"
                  control={control}
                  rules={{ min: { value: 0, message: 'Must be 0 or greater' } }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Boys' Tickets"
                      type="number"
                      inputProps={{ min: 0 }}
                      error={!!errors.boys_tickets}
                      helperText={errors.boys_tickets?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="girls_tickets"
                  control={control}
                  rules={{ min: { value: 0, message: 'Must be 0 or greater' } }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Girls' Tickets"
                      type="number"
                      inputProps={{ min: 0 }}
                      error={!!errors.girls_tickets}
                      helperText={errors.girls_tickets?.message}
                    />
                  )}
                />
              </Grid>

              {/* Price Breakdown */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <>
                    <Typography variant="h6" gutterBottom>
                      Price Breakdown
                    </Typography>
                    {currentWave && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Using prices from: <strong>{currentWave.name}</strong>
                      </Typography>
                    )}
                    
                    {/* Debug Price Values */}
                    <Box sx={{ p: 1, mb: 2, bgcolor: 'yellow.100', borderRadius: 1, border: '1px solid', borderColor: 'yellow.300' }}>
                      <Typography variant="caption" color="text.secondary">
                        <strong>DEBUG:</strong> Boys Price: ${boysPrice}, Girls Price: ${girlsPrice} | Wave ID: {currentWave?.id}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Boys' Tickets ({boysTickets} × ${boysPrice}): </Typography>
                      <Typography>${boysTickets * boysPrice}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Girls' Tickets ({girlsTickets} × ${girlsPrice}): </Typography>
                      <Typography>${girlsTickets * girlsPrice}</Typography>
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="h6" fontWeight="bold">
                        Total:
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        ${totalAmount}
                      </Typography>
                    </Box>
                  </>
                </Paper>
              </Grid>

              {/* Receipt Upload */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Payment Receipt
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12}>
                <Paper
                  {...getRootProps()}
                  sx={{
                    p: 3,
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'grey.300',
                    bgcolor: isDragActive ? 'primary.50' : 'grey.50',
                    cursor: 'pointer',
                    textAlign: 'center',
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'primary.50',
                    },
                  }}
                >
                  <input {...getInputProps()} />
                  <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {isDragActive ? 'Drop the receipt here' : 'Drag & drop receipt here'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    or click to select file (PDF, JPG, PNG)
                  </Typography>
                </Paper>
              </Grid>

              {uploadPreview && (
                <Grid item xs={12}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <>
                      <Typography variant="subtitle1" gutterBottom>
                        <Receipt sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Receipt Preview
                      </Typography>
                      <Box
                        component="img"
                        src={uploadPreview}
                        alt="Receipt preview"
                        sx={{
                          maxWidth: '100%',
                          maxHeight: 200,
                          objectFit: 'contain',
                          border: '1px solid',
                          borderColor: 'grey.300',
                          borderRadius: 1,
                        }}
                      />
                    </>
                  </Paper>
                </Grid>
              )}

              {/* Submit Button */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={createOrderMutation.isPending || !uploadedFile}
                    sx={{ mt: 2 }}
                  >
                    {createOrderMutation.isPending ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : (
                      'Submit Order'
                    )}
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => {
                      reset();
                      setUploadedFile(null);
                      setUploadPreview(null);
                      localStorage.removeItem('customerFormData');
                    }}
                    sx={{ mt: 2, minWidth: 120 }}
                  >
                    Clear Form
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CustomerForm; 