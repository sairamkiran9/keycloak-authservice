import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import OAuthCallback from '../OAuthCallback';
import { AuthProvider } from '../../context/AuthContext';
import api from '../../services/authService';

// Mock the API service
vi.mock('../../services/authService', () => ({
  default: {
    post: vi.fn()
  }
}));

// Mock react-router-dom hooks
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [new URLSearchParams('?code=test-auth-code')]
  };
});

// Mock AuthContext
const mockSetTokens = vi.fn();
vi.mock('../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    setTokens: mockSetTokens
  })
}));

describe('OAuthCallback', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        setItem: vi.fn(),
        getItem: vi.fn(),
        removeItem: vi.fn(),
      },
      writable: true
    });
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <OAuthCallback />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders loading state initially', () => {
    renderComponent();
    
    expect(screen.getByText('🔄 Signing you in...')).toBeInTheDocument();
    expect(screen.getByText('Please wait while we complete your authentication.')).toBeInTheDocument();
  });

  it('handles successful OAuth callback', async () => {
    const mockTokenResponse = {
      data: {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        expires_in: 900
      }
    };

    api.post.mockResolvedValueOnce(mockTokenResponse);

    renderComponent();

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/oauth/callback', {
        code: 'test-auth-code'
      });
    });

    await waitFor(() => {
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-access-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'test-refresh-token');
      expect(mockSetTokens).toHaveBeenCalledWith('test-access-token', 'test-refresh-token');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('handles OAuth callback failure', async () => {
    api.post.mockRejectedValueOnce(new Error('Authentication failed'));

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('❌ Authentication failed')).toBeInTheDocument();
      expect(screen.getByText('Redirecting to login...')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    }, { timeout: 3000 });
  });
});

// Test with missing authorization code
describe('OAuthCallback - Missing Code', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('handles missing authorization code', async () => {
    // Mock useSearchParams to return empty params
    vi.doMock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useSearchParams: () => [new URLSearchParams('')]
      };
    });

    const { OAuthCallback: TestComponent } = await import('../OAuthCallback');
    
    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('❌ No authorization code received')).toBeInTheDocument();
      expect(screen.getByText('Redirecting to login...')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    }, { timeout: 3000 });
  });
});