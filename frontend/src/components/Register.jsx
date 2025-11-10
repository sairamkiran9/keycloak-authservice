import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';
import {
  validateUsername,
  validateEmail,
  validatePasswordStrength,
  validateName,
  getPasswordStrengthColor
} from '../utils/validators';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState('none');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error for this field
    setErrors(prev => ({
      ...prev,
      [name]: ''
    }));
    setServerError('');

    // Update password strength in real-time
    if (name === 'password') {
      const result = validatePasswordStrength(value);
      setPasswordStrength(result.strength || 'none');
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validate username
    const usernameResult = validateUsername(formData.username);
    if (!usernameResult.valid) {
      newErrors.username = usernameResult.error;
    }

    // Validate email
    const emailResult = validateEmail(formData.email);
    if (!emailResult.valid) {
      newErrors.email = emailResult.error;
    }

    // Validate password
    const passwordResult = validatePasswordStrength(formData.password);
    if (!passwordResult.valid) {
      newErrors.password = passwordResult.error;
    }

    // Validate password confirmation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Validate optional fields
    if (formData.firstName) {
      const firstNameResult = validateName(formData.firstName, 'First name');
      if (!firstNameResult.valid) {
        newErrors.firstName = firstNameResult.error;
      }
    }

    if (formData.lastName) {
      const lastNameResult = validateName(formData.lastName, 'Last name');
      if (!lastNameResult.valid) {
        newErrors.lastName = lastNameResult.error;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName
      });

      // Registration successful - redirect to login
      navigate('/login', {
        state: {
          message: 'Registration successful! Please login with your credentials.',
          username: formData.username
        }
      });
    } catch (error) {
      // Parse error message
      try {
        const errorDetails = JSON.parse(error.message);
        setErrors(errorDetails);
      } catch {
        setServerError(error.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Create Account</h1>
        <p style={styles.subtitle}>Keycloak Authentication Service</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          {/* Username */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Username *</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="johndoe"
              required
              style={{
                ...styles.input,
                borderColor: errors.username ? '#ff4444' : '#ddd'
              }}
            />
            {errors.username && (
              <span style={styles.errorText}>{errors.username}</span>
            )}
          </div>

          {/* Email */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="john@example.com"
              required
              style={{
                ...styles.input,
                borderColor: errors.email ? '#ff4444' : '#ddd'
              }}
            />
            {errors.email && (
              <span style={styles.errorText}>{errors.email}</span>
            )}
          </div>

          {/* Password */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Password *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Min 8 chars, 1 upper, 1 lower, 1 number"
              required
              style={{
                ...styles.input,
                borderColor: errors.password ? '#ff4444' : '#ddd'
              }}
            />
            {formData.password && (
              <div style={styles.strengthBar}>
                <div
                  style={{
                    ...styles.strengthFill,
                    width: passwordStrength === 'strong' ? '100%' :
                           passwordStrength === 'medium' ? '66%' :
                           passwordStrength === 'weak' ? '33%' : '0%',
                    backgroundColor: getPasswordStrengthColor(passwordStrength)
                  }}
                />
              </div>
            )}
            {formData.password && (
              <span style={{
                ...styles.strengthText,
                color: getPasswordStrengthColor(passwordStrength)
              }}>
                {passwordStrength.charAt(0).toUpperCase() + passwordStrength.slice(1)} password
              </span>
            )}
            {errors.password && (
              <span style={styles.errorText}>{errors.password}</span>
            )}
          </div>

          {/* Confirm Password */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Confirm Password *</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Re-enter your password"
              required
              style={{
                ...styles.input,
                borderColor: errors.confirmPassword ? '#ff4444' : '#ddd'
              }}
            />
            {errors.confirmPassword && (
              <span style={styles.errorText}>{errors.confirmPassword}</span>
            )}
          </div>

          {/* First Name (Optional) */}
          <div style={styles.formGroup}>
            <label style={styles.label}>First Name</label>
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              placeholder="John"
              style={{
                ...styles.input,
                borderColor: errors.firstName ? '#ff4444' : '#ddd'
              }}
            />
            {errors.firstName && (
              <span style={styles.errorText}>{errors.firstName}</span>
            )}
          </div>

          {/* Last Name (Optional) */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Last Name</label>
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              placeholder="Doe"
              style={{
                ...styles.input,
                borderColor: errors.lastName ? '#ff4444' : '#ddd'
              }}
            />
            {errors.lastName && (
              <span style={styles.errorText}>{errors.lastName}</span>
            )}
          </div>

          {/* Server Error */}
          {serverError && (
            <div style={styles.error}>
              {serverError}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        {/* Login Link */}
        <div style={styles.footer}>
          Already have an account?{' '}
          <Link to="/login" style={styles.link}>
            Login here
          </Link>
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
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '500px',
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
  strengthBar: {
    width: '100%',
    height: '4px',
    backgroundColor: '#eee',
    borderRadius: '2px',
    marginTop: '8px',
    overflow: 'hidden',
  },
  strengthFill: {
    height: '100%',
    transition: 'width 0.3s ease, background-color 0.3s ease',
  },
  strengthText: {
    fontSize: '12px',
    marginTop: '4px',
    display: 'block',
  },
  errorText: {
    fontSize: '12px',
    color: '#ff4444',
    marginTop: '4px',
    display: 'block',
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
    marginTop: '10px',
  },
  error: {
    padding: '10px',
    marginBottom: '20px',
    backgroundColor: '#fee',
    color: '#c00',
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
};

export default Register;