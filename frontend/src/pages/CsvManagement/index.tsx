import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
} from '@mui/material';

const CsvManagement: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        CSV Management
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Venmo Transactions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload and manage Venmo CSV files
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Zelle Transactions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload and manage Chase/Zelle CSV files
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload History
          </Typography>
          <Typography variant="body2" color="text.secondary">
            CSV management functionality coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CsvManagement; 