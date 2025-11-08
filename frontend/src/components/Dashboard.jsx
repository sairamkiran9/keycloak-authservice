import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/authService';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogout = async () => {
    await logout();
  };

  const testProtectedEndpoint = async () => {
    setLoading(true);
    setError('');
    setApiResponse(null);

    try {
      const data = await authService.callProtectedAPI('/api/protected');
      setApiResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testAdminEndpoint = async () => {
    setLoading(true);
    setError('');
    setApiResponse(null);

    try {
      const data = await authService.callProtectedAPI('/api/admin');
      setApiResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testUserDataEndpoint = async () => {
    setLoading(true);
    setError('');
    setApiResponse(null);

    try {
      const data = await authService.callProtectedAPI('/api/user-data');
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
        <h1>Dashboard</h1>
        <button onClick={handleLogout} style={styles.logoutButton}>
          Logout
        </button>
      </div>

      <div style={styles.section}>
        <h2>User Information</h2>
        <div style={styles.card}>
          <table style={styles.table}>
            <tbody>
              <tr>
                <td style={styles.labelCell}><strong>User ID:</strong></td>
                <td>{user?.user_id || 'N/A'}</td>
              </tr>
              <tr>
                <td style={styles.labelCell}><strong>Username:</strong></td>
                <td>{user?.username || 'N/A'}</td>
              </tr>
              <tr>
                <td style={styles.labelCell}><strong>Email:</strong></td>
                <td>{user?.email || 'N/A'}</td>
              </tr>
              <tr>
                <td style={styles.labelCell}><strong>Roles:</strong></td>
                <td>{user?.roles?.join(', ') || 'None'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style={styles.section}>
        <h2>Test API Endpoints</h2>
        <div style={styles.buttonGroup}>
          <button
            onClick={testProtectedEndpoint}
            disabled={loading}
            style={styles.testButton}
          >
            Test /api/protected
          </button>
          <button
            onClick={testAdminEndpoint}
            disabled={loading}
            style={styles.testButton}
          >
            Test /api/admin
          </button>
          <button
            onClick={testUserDataEndpoint}
            disabled={loading}
            style={styles.testButton}
          >
            Test /api/user-data
          </button>
        </div>

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
        <h2>Raw Token Claims</h2>
        <div style={styles.card}>
          <pre style={styles.pre}>
            {JSON.stringify(user, null, 2)}
          </pre>
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
  logoutButton: {
    padding: '10px 20px',
    fontSize: '14px',
    color: 'white',
    backgroundColor: '#dc3545',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  section: {
    marginBottom: '40px',
  },
  card: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  labelCell: {
    width: '150px',
    padding: '8px 0',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  testButton: {
    padding: '10px 20px',
    fontSize: '14px',
    color: 'white',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
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
};

export default Dashboard;