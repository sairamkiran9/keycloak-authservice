const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class AuthService {
  // Login
  async login(username, password) {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user_info', JSON.stringify(data.user_info));

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  // Logout
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        await fetch(`${API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_info');
    }
  }

  // Get current user
  getCurrentUser() {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }

  // Check if authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  // Get access token
  getAccessToken() {
    return localStorage.getItem('access_token');
  }

  // Refresh token
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        throw new Error('No refresh token');
      }

      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Token refresh failed');
      }

      // Update tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);

      return data;
    } catch (error) {
      console.error('Refresh token error:', error);
      this.logout();
      throw error;
    }
  }

  // Fetch user info from API
  async getUserInfo() {
    try {
      const response = await fetch(`${API_URL}/auth/userinfo`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Try to refresh token
          await this.refreshToken();
          // Retry the request
          return this.getUserInfo();
        }
        throw new Error('Failed to fetch user info');
      }

      return await response.json();
    } catch (error) {
      console.error('Get user info error:', error);
      throw error;
    }
  }

  // Call protected API endpoint
  async callProtectedAPI(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${this.getAccessToken()}`,
        },
      });

      if (response.status === 401) {
        // Try to refresh token
        await this.refreshToken();
        // Retry the request
        return this.callProtectedAPI(endpoint, options);
      }

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'API call failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  }
}

export default new AuthService();