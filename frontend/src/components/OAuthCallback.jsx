import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/authService';

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');

    if (!code) {
      setError('No authorization code received');
      setTimeout(() => navigate('/login'), 2000);
      return;
    }

    // Exchange code for tokens
    api.post('/auth/oauth/callback', { code })
      .then(response => {
        const { access_token, refresh_token } = response;

        // Store tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Update auth context
        if (setTokens) {
          setTokens(access_token, refresh_token);
        }

        // Redirect to dashboard
        navigate('/dashboard');
      })
      .catch(err => {
        console.error('OAuth callback failed', err);
        setError('Authentication failed');
        setTimeout(() => navigate('/login'), 2000);
      });
  }, [searchParams, navigate, setTokens]);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {error ? (
          <>
            <h2>❌ {error}</h2>
            <p>Redirecting to login...</p>
          </>
        ) : (
          <>
            <h2>🔄 Signing you in...</h2>
            <p>Please wait while we complete your authentication.</p>
          </>
        )}
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
    textAlign: 'center',
  }
};

export default OAuthCallback;