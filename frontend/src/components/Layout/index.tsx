import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  IconButton,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Analytics,
  Storage,
  Logout,
  Login,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
    handleMenuClose();
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    handleMenuClose();
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ background: 'linear-gradient(135deg, #000080 0%, #000040 100%)' }}>
        <Toolbar>
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 1,
              color: 'white',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          >
            <span style={{ fontFamily: 'Times New Roman, serif', fontWeight: 'bold' }}>
              ΔΕΨ
            </span>{' '}
            Ticket Verifier
          </Typography>

          {isMobile ? (
            <>
              <IconButton
                size="large"
                edge="end"
                color="inherit"
                aria-label="menu"
                onClick={handleMenuOpen}
              >
                <MenuIcon />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                <MenuItem onClick={() => handleNavigation('/')}>
                  Submit Order
                </MenuItem>
                {isAuthenticated ? (
                  <>
                    <MenuItem onClick={() => handleNavigation('/admin')}>
                      <Dashboard sx={{ mr: 1 }} />
                      Admin Dashboard
                    </MenuItem>
                    <MenuItem onClick={() => handleNavigation('/analytics')}>
                      <Analytics sx={{ mr: 1 }} />
                      Analytics
                    </MenuItem>
                    <MenuItem onClick={() => handleNavigation('/csv-management')}>
                      <Storage sx={{ mr: 1 }} />
                      CSV Management
                    </MenuItem>
                    <MenuItem onClick={handleLogout}>
                      <Logout sx={{ mr: 1 }} />
                      Logout
                    </MenuItem>
                  </>
                ) : (
                  <MenuItem onClick={() => handleNavigation('/login')}>
                    <Login sx={{ mr: 1 }} />
                    Admin Login
                  </MenuItem>
                )}
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                color="inherit"
                onClick={() => navigate('/')}
                sx={{
                  color: isActive('/') ? '#FFD700' : 'white',
                  '&:hover': { color: '#FFD700' },
                }}
              >
                Submit Order
              </Button>
              {isAuthenticated ? (
                <>
                  <Button
                    color="inherit"
                    onClick={() => navigate('/admin')}
                    sx={{
                      color: isActive('/admin') ? '#FFD700' : 'white',
                      '&:hover': { color: '#FFD700' },
                    }}
                  >
                    Admin Dashboard
                  </Button>
                  <Button
                    color="inherit"
                    onClick={() => navigate('/analytics')}
                    sx={{
                      color: isActive('/analytics') ? '#FFD700' : 'white',
                      '&:hover': { color: '#FFD700' },
                    }}
                  >
                    Analytics
                  </Button>
                  <Button
                    color="inherit"
                    onClick={() => navigate('/csv-management')}
                    sx={{
                      color: isActive('/csv-management') ? '#FFD700' : 'white',
                      '&:hover': { color: '#FFD700' },
                    }}
                  >
                    CSV Management
                  </Button>
                  <Button
                    color="inherit"
                    onClick={handleLogout}
                    sx={{
                      color: 'white',
                      '&:hover': { color: '#FFD700' },
                    }}
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <Button
                  color="inherit"
                  onClick={() => navigate('/login')}
                  sx={{
                    color: isActive('/login') ? '#FFD700' : 'white',
                    '&:hover': { color: '#FFD700' },
                  }}
                >
                  Admin Login
                </Button>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout; 