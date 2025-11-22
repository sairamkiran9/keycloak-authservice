import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Login from '../Login';
import { AuthProvider } from '../../context/AuthContext';
import api from '../../services/authService';

// Mock the API service
vi.mock('../../services/authService', () => ({
  default: {
    get: vi.fn(),
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
    useLocation: () => ({ state: null })
  };
});

// Mock AuthContext
vi.mock('../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    login: vi.fn()
  })
}));

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('Login - SSO Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.location.href = '';
  });

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('fetches and displays SSO providers on mount', async () => {
    const mockProviders = {
      data: {
        providers: [
          {
            id: 'google',
            name: 'Google',
            displayName: 'Continue with Google'
          }
        ]
      }
    };

    api.get.mockResolvedValueOnce(mockProviders);

    renderLogin();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/auth/sso/providers');
    });

    await waitFor(() => {
      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
      expect(screen.getByText('OR')).toBeInTheDocument();
    });
  });

  it('does not show SSO section when no providers available', async () => {
    const mockProviders = {
      data: {
        providers: []
      }
    };

    api.get.mockResolvedValueOnce(mockProviders);

    renderLogin();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/auth/sso/providers');
    });

    // Should not show OR divider or SSO buttons
    expect(screen.queryByText('OR')).not.toBeInTheDocument();
    expect(screen.queryByText('Continue with Google')).not.toBeInTheDocument();
  });

  it('handles SSO provider fetch error gracefully', async () => {
    api.get.mockRejectedValueOnce(new Error('Network error'));

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    renderLogin();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/auth/sso/providers');
    });

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch SSO providers', expect.any(Error));
    });

    // Should not show SSO section on error
    expect(screen.queryByText('OR')).not.toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it('initiates Google SSO login when button clicked', async () => {
    const mockProviders = {
      data: {
        providers: [
          {
            id: 'google',
            name: 'Google',
            displayName: 'Continue with Google'
          }
        ]
      }
    };

    const mockSSOResponse = {
      data: {
        redirect_url: 'https://keycloak.example.com/auth/realms/test/protocol/openid-connect/auth?client_id=test&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid+profile+email&kc_idp_hint=google'
      }
    };

    api.get
      .mockResolvedValueOnce(mockProviders)
      .mockResolvedValueOnce(mockSSOResponse);

    renderLogin();

    // Wait for providers to load
    await waitFor(() => {
      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    });

    // Click Google SSO button
    const googleButton = screen.getByText('Continue with Google');
    fireEvent.click(googleButton);

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/auth/sso/login/google');
    });

    await waitFor(() => {
      expect(window.location.href).toBe(mockSSOResponse.data.redirect_url);
    });
  });

  it('shows error when SSO login fails', async () => {
    const mockProviders = {
      data: {
        providers: [
          {
            id: 'google',
            name: 'Google',
            displayName: 'Continue with Google'
          }
        ]
      }
    };

    api.get
      .mockResolvedValueOnce(mockProviders)
      .mockRejectedValueOnce(new Error('SSO service unavailable'));

    renderLogin();

    // Wait for providers to load
    await waitFor(() => {
      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    });

    // Click Google SSO button
    const googleButton = screen.getByText('Continue with Google');
    fireEvent.click(googleButton);

    await waitFor(() => {
      expect(screen.getByText('❌ SSO login failed')).toBeInTheDocument();
    });
  });

  it('disables SSO button when loading', async () => {
    const mockProviders = {
      data: {
        providers: [
          {
            id: 'google',
            name: 'Google',
            displayName: 'Continue with Google'
          }
        ]
      }
    };

    api.get.mockResolvedValueOnce(mockProviders);

    renderLogin();

    // Wait for providers to load
    await waitFor(() => {
      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    });

    // Simulate loading state by clicking login button first
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    // Google button should be disabled during loading
    const googleButton = screen.getByText('Continue with Google').closest('button');
    expect(googleButton).toBeDisabled();
  });

  it('renders multiple SSO providers when available', async () => {
    const mockProviders = {
      data: {
        providers: [
          {
            id: 'google',
            name: 'Google',
            displayName: 'Continue with Google'
          },
          {
            id: 'github',
            name: 'GitHub',
            displayName: 'Continue with GitHub'
          }
        ]
      }
    };

    api.get.mockResolvedValueOnce(mockProviders);

    renderLogin();

    await waitFor(() => {
      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
      expect(screen.getByText('Continue with GitHub')).toBeInTheDocument();
    });
  });
});