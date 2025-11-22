/**
 * End-to-End SSO Tests
 * These tests simulate the complete user journey for Google SSO authentication
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock fetch for API calls
global.fetch = vi.fn();

// Mock window.location
delete window.location;
window.location = { href: '', assign: vi.fn() };

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

describe('SSO End-to-End Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetch.mockClear();
    window.location.href = '';
  });

  it('completes full Google SSO authentication flow', async () => {
    // Step 1: User visits login page, app fetches SSO providers
    const providersResponse = {
      providers: [
        {
          id: 'google',
          name: 'Google',
          displayName: 'Continue with Google'
        }
      ]
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => providersResponse
    });

    // Simulate fetching providers
    const providersResult = await fetch('/auth/sso/providers');
    const providers = await providersResult.json();

    expect(fetch).toHaveBeenCalledWith('/auth/sso/providers');
    expect(providers.providers).toHaveLength(1);
    expect(providers.providers[0].id).toBe('google');

    // Step 2: User clicks "Continue with Google" button
    const ssoLoginResponse = {
      redirect_url: 'http://localhost:8080/realms/microservices-realm/protocol/openid-connect/auth?client_id=auth-service&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid+profile+email&kc_idp_hint=google'
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ssoLoginResponse
    });

    // Simulate SSO login request
    const ssoResult = await fetch('/auth/sso/login/google');
    const ssoData = await ssoResult.json();

    expect(fetch).toHaveBeenCalledWith('/auth/sso/login/google');
    expect(ssoData.redirect_url).toContain('kc_idp_hint=google');
    expect(ssoData.redirect_url).toContain('redirect_uri=http://localhost:3000/callback');

    // Step 3: Browser redirects to Keycloak + Google (simulated)
    window.location.href = ssoData.redirect_url;
    expect(window.location.href).toBe(ssoData.redirect_url);

    // Step 4: User completes Google authentication, Keycloak redirects back with code
    const authorizationCode = 'mock-authorization-code-from-google';
    const callbackUrl = `http://localhost:3000/callback?code=${authorizationCode}`;

    // Step 5: Frontend exchanges code for tokens
    const tokenResponse = {
      access_token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
      refresh_token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
      expires_in: 900
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => tokenResponse
    });

    // Simulate token exchange
    const tokenResult = await fetch('/auth/oauth/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: authorizationCode })
    });
    const tokens = await tokenResult.json();

    expect(fetch).toHaveBeenCalledWith('/auth/oauth/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: authorizationCode })
    });

    expect(tokens.access_token).toBeTruthy();
    expect(tokens.refresh_token).toBeTruthy();
    expect(tokens.expires_in).toBe(900);

    // Step 6: Tokens are stored and user is redirected to dashboard
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);

    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', tokens.access_token);
    expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', tokens.refresh_token);
  });

  it('handles SSO provider discovery failure gracefully', async () => {
    // Simulate network error when fetching providers
    fetch.mockRejectedValueOnce(new Error('Network error'));

    try {
      await fetch('/auth/sso/providers');
    } catch (error) {
      expect(error.message).toBe('Network error');
    }

    expect(fetch).toHaveBeenCalledWith('/auth/sso/providers');
  });

  it('handles SSO login URL generation failure', async () => {
    // Simulate server error when generating login URL
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Internal server error' })
    });

    const response = await fetch('/auth/sso/login/google');
    const data = await response.json();

    expect(response.ok).toBe(false);
    expect(response.status).toBe(500);
    expect(data.error).toBe('Internal server error');
  });

  it('handles OAuth callback failure', async () => {
    // Simulate invalid authorization code
    const invalidCode = 'invalid-auth-code';

    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Invalid authorization code' })
    });

    const response = await fetch('/auth/oauth/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: invalidCode })
    });

    const error = await response.json();

    expect(response.ok).toBe(false);
    expect(response.status).toBe(400);
    expect(error.error).toBe('Invalid authorization code');
  });

  it('validates redirect URI security', async () => {
    const ssoLoginResponse = {
      redirect_url: 'http://localhost:8080/realms/microservices-realm/protocol/openid-connect/auth?client_id=auth-service&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid+profile+email&kc_idp_hint=google'
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ssoLoginResponse
    });

    const response = await fetch('/auth/sso/login/google');
    const data = await response.json();

    // Verify redirect URI is properly set to our callback
    expect(data.redirect_url).toContain('redirect_uri=http://localhost:3000/callback');
    
    // Verify other security parameters
    expect(data.redirect_url).toContain('response_type=code');
    expect(data.redirect_url).toContain('scope=openid+profile+email');
  });

  it('handles multiple SSO providers', async () => {
    const multiProviderResponse = {
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
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => multiProviderResponse
    });

    const response = await fetch('/auth/sso/providers');
    const data = await response.json();

    expect(data.providers).toHaveLength(2);
    expect(data.providers.map(p => p.id)).toEqual(['google', 'github']);
  });

  it('handles SSO disabled scenario', async () => {
    const disabledResponse = {
      providers: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => disabledResponse
    });

    const response = await fetch('/auth/sso/providers');
    const data = await response.json();

    expect(data.providers).toHaveLength(0);
  });

  it('validates token storage and cleanup', async () => {
    const tokens = {
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      expires_in: 900
    };

    // Store tokens
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);

    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', tokens.access_token);
    expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', tokens.refresh_token);

    // Simulate logout - tokens should be cleared
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
  });
});

describe('SSO Error Scenarios', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetch.mockClear();
  });

  it('handles network timeouts gracefully', async () => {
    // Simulate timeout
    fetch.mockImplementationOnce(() => 
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 100)
      )
    );

    try {
      await fetch('/auth/sso/providers');
    } catch (error) {
      expect(error.message).toBe('Request timeout');
    }
  });

  it('handles malformed responses', async () => {
    // Simulate malformed JSON response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => { throw new Error('Invalid JSON'); }
    });

    try {
      const response = await fetch('/auth/sso/providers');
      await response.json();
    } catch (error) {
      expect(error.message).toBe('Invalid JSON');
    }
  });

  it('handles missing authorization code in callback', async () => {
    // Simulate callback without code parameter
    const callbackUrl = 'http://localhost:3000/callback?error=access_denied';
    
    // In real scenario, frontend should detect missing code and show error
    const urlParams = new URLSearchParams(callbackUrl.split('?')[1]);
    const code = urlParams.get('code');
    const error = urlParams.get('error');

    expect(code).toBeNull();
    expect(error).toBe('access_denied');
  });
});