import { useState } from 'react';
import { Link } from 'react-router-dom';

const PublicPage = () => {
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const testPublicEndpoint = async () => {
    setLoading(true);
    setError('');
    setApiResponse(null);

    try {
      const response = await fetch('http://localhost:5000/api/public');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'API call failed');
      }

      setApiResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>Public Page</h1>
        <Link to="/login" style={styles.loginLink}>
          Login
        </Link>
      </div>

      <div style={styles.section}>
        <p style={styles.description}>
          This is a public page accessible without authentication.
        </p>
      </div>

      <div style={styles.section}>
        <h2>Test Public API Endpoint</h2>
        <button
          onClick={testPublicEndpoint}
          disabled={loading}
          style={styles.button}
        >
          Test /api/public
        </button>

        {loading && <p>Loading...</p>}

        {error && (
          <div style={styles.error}>
            ❌ Error: {error}
          </div>
        )}

        {apiResponse && (
          <div style={styles.success}>
            <h3>API Response:</h3>
            <pre style={styles.pre}>
              {JSON.stringify(apiResponse, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div style={styles.section}>
        <h2>Authentication Info</h2>
        <div style={styles.card}>
          <p>This page does not require authentication.</p>
          <p>
            To test protected endpoints, please{' '}
            <Link to="/login" style={styles.link}>
              login
            </Link>
            .
          </p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1000px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    paddingBottom: '20px',
    borderBottom: '2px solid #eee',
  },
  loginLink: {
    padding: '10px 20px',
    fontSize: '14px',
    color: 'white',
    backgroundColor: '#007bff',
    textDecoration: 'none',
    borderRadius: '4px',
  },
  section: {
    marginBottom: '40px',
  },
  description: {
    fontSize: '16px',
    color: '#666',
  },
  card: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  button: {
    padding: '10px 20px',
    fontSize: '14px',
    color: 'white',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginBottom: '20px',
  },
  error: {
    padding: '15px',
    backgroundColor: '#fee',
    color: '#c00',
    borderRadius: '4px',
    marginTop: '20px',
  },
  success: {
    padding: '15px',
    backgroundColor: '#efe',
    color: '#060',
    borderRadius: '4px',
    marginTop: '20px',
  },
  pre: {
    backgroundColor: '#f5f5f5',
    padding: '15px',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '12px',
    lineHeight: '1.5',
  },
  link: {
    color: '#007bff',
    textDecoration: 'underline',
  },
};

export default PublicPage;