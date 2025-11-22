import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SSOButton from './SSOButton';
import api from '../services/authService';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [ssoProviders, setSsoProviders] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  // Get success message from navigation state (NEW)
  const successMessage = location.state?.message;
  const prefilledUsername = location.state?.username;

  // Prefill username if provided (NEW)
  useState(() => {
    if (prefilledUsername) {
      setUsername(prefilledUsername);
    }
  }, [prefilledUsername]);

  useEffect(() => {
    // Fetch available SSO providers
    api.get('/auth/sso/providers').then(response => {
      setSsoProviders(response.providers || []);
    }).catch(err => {
      console.error('Failed to fetch SSO providers', err);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error || 'Login failed');
    }

    setLoading(false);
  };

  const handleSSOLogin = async (provider) => {
    try {
      const response = await api.get(`/auth/sso/login/${provider}`);
      // Redirect to Keycloak + Google
      window.location.href = response.redirect_url;
    } catch (error) {
      console.error('SSO login error:', error);
      setError('SSO login failed');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Login</h1>
        <p style={styles.subtitle}>Keycloak Authentication Service</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="testuser"
              required
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password123"
              required
              style={styles.input}
            />
          </div>

          {/* Success Message (NEW) */}
          {successMessage && (
            <div style={styles.success}>
              ✓ {successMessage}
            </div>
          )}

          {error && (
            <div style={styles.error}>
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* SSO Options */}
        {ssoProviders.length > 0 && (
          <>
            <div style={styles.divider}>
              <span style={styles.dividerText}>OR</span>
            </div>

            <div style={styles.ssoButtons}>
              {ssoProviders.map(provider => (
                <SSOButton
                  key={provider.id}
                  provider={provider}
                  onClick={handleSSOLogin}
                  loading={loading}
                />
              ))}
            </div>
          </>
        )}

        {/* Registration Link (NEW) */}
        <div style={styles.footer}>
          Don't have an account?{' '}
          <Link to="/register" style={styles.link}>
            Sign up here
          </Link>
        </div>

        <div style={styles.hint}>
          <p><strong>Test Users:</strong></p>
          <p>testuser / password123 (role: user)</p>
          <p>adminuser / admin123 (roles: user, admin)</p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    margin: '0 0 10px 0',
    fontSize: '24px',
    textAlign: 'center',
  },
  subtitle: {
    margin: '0 0 30px 0',
    fontSize: '14px',
    color: '#666',
    textAlign: 'center',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '500',
  },
  input: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxSizing: 'border-box',
  },
  button: {
    padding: '12px',
    fontSize: '16px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  error: {
    padding: '10px',
    marginBottom: '20px',
    backgroundColor: '#fee',
    color: '#c00',
    borderRadius: '4px',
    fontSize: '14px',
  },
  success: {
    padding: '10px',
    marginBottom: '20px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    fontSize: '14px',
  },
  footer: {
    marginTop: '20px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#666',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
  },
  hint: {
    marginTop: '30px',
    padding: '15px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#666',
    lineHeight: '1.6',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '20px 0',
    color: '#999',
  },
  dividerText: {
    margin: '0 10px',
    fontSize: '12px',
  },
  ssoButtons: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '20px',
  },
};

export default Login;