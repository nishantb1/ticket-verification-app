export interface Order {
  id: number;
  uuid: string;
  name: string;
  email: string;
  referral?: string;
  boys_count: number;
  girls_count: number;
  wave_id?: number;
  expected_amount: number;
  ocr_amount?: number;
  ocr_date?: string;
  ocr_name?: string;
  status: 'Pending' | 'Approved' | 'Rejected' | 'Completed' | 'Verified';
  receipt_path?: string;
  created_at: string;
  notes?: string;
  phone?: string;
  wave_name?: string;
  matched_transaction?: Transaction;
}

export interface Wave {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  boys_price: number;
  girls_price: number;
  is_active: boolean;
  created_at: string;
}

export interface Transaction {
  id: number;
  datetime: string;
  type: string;
  note: string;
  from_user: string;
  to_user: string;
  amount: number;
  fee: number;
  net_amount: number;
  csv_filename: string;
  csv_upload_date: string;
  updated_at: string;
}

export interface VenmoTransaction extends Transaction {
  // Venmo specific fields
}

export interface ZelleTransaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  type: string;
  balance: number;
  payer_identifier: string;
  csv_filename: string;
  csv_upload_date: string;
  updated_at: string;
}

export interface CsvUpload {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  upload_type: 'venmo' | 'zelle';
  records_processed: number;
  new_records: number;
  updated_records: number;
  admin_user: string;
  upload_date: string;
  status: 'success' | 'error' | 'partial';
}

export interface AdminUser {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Analytics {
  total_orders: number;
  pending_orders: number;
  approved_orders: number;
  rejected_orders: number;
  total_revenue: number;
  orders_by_status: Record<string, number>;
  orders_by_wave: Record<string, number>;
  recent_orders: Order[];
  venmo_transactions: number;
  zelle_transactions: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  admin_user?: AdminUser;
}

export interface OrderFormData {
  name: string;
  email: string;
  boys_tickets: number;
  girls_tickets: number;
  receipt: File | null;
}

export interface WaveFormData {
  name: string;
  start_date: string;
  end_date: string;
  boys_price: number;
  girls_price: number;
  is_active?: boolean;
}

export interface FileUploadResponse {
  success: boolean;
  filename?: string;
  message?: string;
  error?: string;
}

export interface MatchResult {
  success: boolean;
  matched: boolean;
  transaction?: Transaction;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface SearchFilters {
  status?: string;
  wave_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }[];
} 