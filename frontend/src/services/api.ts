import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  Order, 
  Wave, 
  Transaction, 
  VenmoTransaction, 
  ZelleTransaction,
  CsvUpload,
  Analytics,
  LoginRequest,
  LoginResponse,
  OrderFormData,
  WaveFormData,
  ApiResponse,
  PaginatedResponse,
  SearchFilters
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    console.log('Initializing API Service...');
    console.log('Base URL:', process.env.REACT_APP_API_URL || 'http://localhost:5000/api');
    
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // This is crucial for session-based auth
    });
    
    console.log('Axios instance created:', this.api);
    
    // Add request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        // For session-based auth, we don't need to add headers
        // The session cookie will be automatically sent by the browser
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login', credentials);
    if (response.data.success) {
      // Dispatch auth state change event
      window.dispatchEvent(new Event('authStateChanged'));
    }
    return response.data;
  }

  validateSession = async (): Promise<{ success: boolean; authenticated: boolean }> => {
    const response: AxiosResponse<{ success: boolean; authenticated: boolean }> = await this.api.get('/auth/validate');
    return response.data;
  }

  logout = async (): Promise<void> => {
    await this.api.post('/auth/logout');
    // Dispatch auth state change event
    window.dispatchEvent(new Event('authStateChanged'));
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  }

  // Orders
  getOrders = async (filters?: SearchFilters): Promise<PaginatedResponse<Order>> => {
    const response: AxiosResponse<PaginatedResponse<Order>> = await this.api.get('/orders', {
      params: filters,
    });
    return response.data;
  }

  getOrder = async (id: number): Promise<Order> => {
    const response: AxiosResponse<Order> = await this.api.get(`/orders/${id}`);
    return response.data;
  }

  createOrder = async (orderData: OrderFormData): Promise<ApiResponse<Order>> => {
    const formData = new FormData();
    formData.append('name', orderData.name);
    formData.append('email', orderData.email);
    formData.append('boys_tickets', orderData.boys_tickets.toString());
    formData.append('girls_tickets', orderData.girls_tickets.toString());
    if (orderData.receipt) {
      formData.append('receipt', orderData.receipt);
    }

    const response: AxiosResponse<ApiResponse<Order>> = await this.api.post('/orders', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  approveOrder = async (id: number): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.post(`/orders/${id}/approve`);
    return response.data;
  }

  rejectOrder = async (id: number): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.post(`/orders/${id}/reject`);
    return response.data;
  }

  deleteOrder = async (id: number): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.delete(`/orders/${id}`);
    return response.data;
  }

  updateOrder = async (id: number, orderData: Partial<Order>): Promise<ApiResponse<Order>> => {
    const response: AxiosResponse<ApiResponse<Order>> = await this.api.put(`/orders/${id}`, orderData);
    return response.data;
  }

  // Waves
  getWaves = async (): Promise<Wave[]> => {
    try {
      console.log('getWaves called');
      console.log('this.api:', this.api);
      const response: AxiosResponse<Wave[]> = await this.api.get('/waves');
      return response.data;
    } catch (error) {
      console.error('Error in getWaves:', error);
      throw error;
    }
  }

  getCurrentWave = async (): Promise<Wave | null> => {
    try {
      console.log('getCurrentWave called');
      const response: AxiosResponse<Wave | null> = await this.api.get('/waves/current');
      console.log('getCurrentWave response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getCurrentWave:', error);
      throw error;
    }
  }

  createWave = async (waveData: WaveFormData): Promise<ApiResponse<Wave>> => {
    try {
      console.log('createWave called with data:', waveData);
      console.log('this.api:', this.api);
      const response: AxiosResponse<ApiResponse<Wave>> = await this.api.post('/waves', waveData);
      return response.data;
    } catch (error) {
      console.error('Error in createWave:', error);
      throw error;
    }
  }

  updateWave = async (id: number, waveData: Partial<WaveFormData>): Promise<ApiResponse<Wave>> => {
    try {
      console.log('updateWave called with id:', id, 'data:', waveData);
      console.log('this.api:', this.api);
      const response: AxiosResponse<ApiResponse<Wave>> = await this.api.put(`/waves/${id}`, waveData);
      return response.data;
    } catch (error) {
      console.error('Error in updateWave:', error);
      throw error;
    }
  }

  deleteWave = async (id: number): Promise<ApiResponse<void>> => {
    try {
      console.log('deleteWave called with id:', id);
      console.log('this.api:', this.api);
      const response: AxiosResponse<ApiResponse<void>> = await this.api.delete(`/waves/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error in deleteWave:', error);
      throw error;
    }
  }

  // Transactions
  async getVenmoTransactions(): Promise<VenmoTransaction[]> {
    const response: AxiosResponse<VenmoTransaction[]> = await this.api.get('/transactions/venmo');
    return response.data;
  }

  async getZelleTransactions(): Promise<ZelleTransaction[]> {
    const response: AxiosResponse<ZelleTransaction[]> = await this.api.get('/transactions/zelle');
    return response.data;
  }

  // CSV Management
  async uploadCsv(file: File): Promise<ApiResponse<CsvUpload>> {
    const formData = new FormData();
    formData.append('csv_file', file);

    const response: AxiosResponse<ApiResponse<CsvUpload>> = await this.api.post('/csv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getCsvUploads(): Promise<CsvUpload[]> {
    const response: AxiosResponse<CsvUpload[]> = await this.api.get('/csv/uploads');
    return response.data;
  }

  // Analytics
  async getAnalytics(): Promise<Analytics> {
    const response: AxiosResponse<Analytics> = await this.api.get('/analytics');
    return response.data;
  }

  // Utilities
  async rerunMatching(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await this.api.post('/orders/rerun-matching');
    return response.data;
  }

  async exportOrders(): Promise<Blob> {
    const response: AxiosResponse<Blob> = await this.api.get('/orders/export', {
      responseType: 'blob',
    });
    return response.data;
  }

  async exportVenmoTransactions(): Promise<Blob> {
    const response: AxiosResponse<Blob> = await this.api.get('/transactions/venmo/export', {
      responseType: 'blob',
    });
    return response.data;
  }

  async exportZelleTransactions(): Promise<Blob> {
    const response: AxiosResponse<Blob> = await this.api.get('/transactions/zelle/export', {
      responseType: 'blob',
    });
    return response.data;
  }

  // File serving
  getReceiptUrl(filename: string): string {
    return `${this.api.defaults.baseURL}/receipts/${filename}`;
  }

  getVerifiedEmails = async (): Promise<{ emails: string[]; email_list: string; count: number; orders: any[] }> => {
    const response: AxiosResponse<{ success: boolean; emails: string[]; email_list: string; count: number; orders: any[] }> = await this.api.get('/orders/verified-emails');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService; 