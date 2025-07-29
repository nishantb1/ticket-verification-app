# 🚀 ΔΕΨ Ticket Verifier - React Edition

A modern React frontend with Flask API backend for automated ticket verification using OCR and transaction matching.

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Flask API     │    │   SQLite DB     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ • Customer Form │    │ • REST API      │    │ • Orders        │
│ • Admin Dashboard│   │ • OCR Processing │   │ • Transactions  │
│ • Analytics     │    │ • File Upload   │    │ • Waves         │
│ • Mobile UI     │    │ • Authentication│    │ • Audit Logs    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ **Features**

### 🎨 **Modern UI/UX**
- **Material-UI Components**: Beautiful, responsive design
- **Real-time Updates**: Live order status updates
- **Mobile-First**: Optimized for all devices
- **Drag & Drop**: Intuitive file uploads
- **Interactive Charts**: Beautiful analytics dashboard

### 🔧 **Technical Features**
- **TypeScript**: Type-safe development
- **React Query**: Efficient data fetching and caching
- **React Hook Form**: Advanced form validation
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors

### 🚀 **Performance**
- **Single Page Application**: Fast navigation
- **Code Splitting**: Optimized bundle sizes
- **Caching**: Smart data caching
- **Lazy Loading**: On-demand component loading

## 📦 **Installation**

### **Prerequisites**
- Node.js 16+ and npm
- Python 3.8+
- Git

### **Quick Start**

1. **Clone the repository**
   ```bash
   git clone https://github.com/nishantb1/ticket-verification-app.git
   cd ticket-verification-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development servers**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🛠️ **Development**

### **Project Structure**
```
zelle_venmo_verifier/
├── frontend/                 # React App
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                # Flask API
│   ├── api.py             # Main API application
│   ├── requirements.txt   # Python dependencies
│   └── wsgi.py           # WSGI configuration
├── shared/                # Shared utilities
└── package.json          # Root package.json
```

### **Available Scripts**

```bash
# Install all dependencies
npm install

# Start both frontend and backend
npm run dev

# Start only backend
npm run dev-backend

# Start only frontend
npm run dev-frontend

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

## 🚀 **Deployment**

### **PythonAnywhere Deployment**

1. **Upload to PythonAnywhere**
   ```bash
   # On your local machine
   git push origin main
   
   # On PythonAnywhere
   git pull origin main
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip3 install -r requirements.txt
   ```

3. **Configure WSGI file**
   - Point to `backend/wsgi.py`
   - Ensure database path is correct

4. **Build frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

5. **Configure static files**
   - Serve React build from `/static/`
   - Update API base URL in production

### **Environment Variables**

Create `.env` files:

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:5000/api
```

**Backend (.env)**
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

## 🔧 **API Endpoints**

### **Authentication**
- `POST /api/auth/login` - Admin login
- `POST /api/auth/logout` - Admin logout
- `POST /api/auth/change-password` - Change password

### **Orders**
- `GET /api/orders` - Get all orders (with pagination)
- `POST /api/orders` - Create new order
- `POST /api/orders/{id}/approve` - Approve order
- `POST /api/orders/{id}/reject` - Reject order
- `DELETE /api/orders/{id}` - Delete order

### **Waves**
- `GET /api/waves` - Get all waves
- `GET /api/waves/current` - Get current active wave
- `POST /api/waves` - Create new wave
- `PUT /api/waves/{id}` - Update wave
- `DELETE /api/waves/{id}` - Delete wave

### **Analytics**
- `GET /api/analytics` - Get analytics data

## 🎨 **UI Components**

### **Customer Form**
- Multi-step form wizard
- Real-time validation
- Drag & drop file upload
- Progress indicators
- Success/error animations

### **Admin Dashboard**
- Interactive Kanban board
- Real-time order updates
- Advanced filtering
- Bulk actions
- Export functionality

### **Analytics**
- Beautiful charts with Recharts
- Real-time data updates
- Interactive filters
- Export capabilities

## 🔒 **Security Features**

- **JWT Authentication**: Secure admin access
- **CORS Protection**: Cross-origin request handling
- **Input Validation**: Server-side validation
- **File Upload Security**: Secure file handling
- **Audit Logging**: Complete action tracking

## 📱 **Mobile Support**

- **Responsive Design**: Works on all screen sizes
- **Touch Optimized**: Mobile-friendly interactions
- **Progressive Web App**: PWA capabilities
- **Offline Support**: Service worker caching

## 🧪 **Testing**

```bash
# Run frontend tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- CustomerForm.test.tsx
```

## 🚀 **Performance Optimizations**

- **Code Splitting**: Lazy-loaded components
- **Image Optimization**: Compressed assets
- **Bundle Analysis**: Webpack bundle analyzer
- **Caching Strategy**: Smart data caching
- **CDN Ready**: Static asset optimization

## 🔧 **Troubleshooting**

### **Common Issues**

1. **CORS Errors**
   - Ensure backend CORS is configured
   - Check API base URL in frontend

2. **Database Issues**
   - Verify database path in backend
   - Check file permissions

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors

4. **Deployment Issues**
   - Verify WSGI configuration
   - Check PythonAnywhere logs

## 📈 **Future Enhancements**

- [ ] **Real-time Notifications**: WebSocket integration
- [ ] **Advanced Analytics**: More detailed reporting
- [ ] **Bulk Operations**: Mass order processing
- [ ] **API Rate Limiting**: Request throttling
- [ ] **Multi-language Support**: Internationalization
- [ ] **Dark Mode**: Theme switching
- [ ] **Offline Mode**: Enhanced PWA features

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

**Built with ❤️ for ΔΕΨ Fraternity** 