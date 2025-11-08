# User Registration Feature - Comprehensive Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Security Considerations](#security-considerations)

---

## Overview

### Feature Description
This guide provides step-by-step instructions to add self-service user registration functionality to the Keycloak authentication service. Users will be able to:
- Register with username, email, and password
- Optionally provide first name and last name
- Automatically receive "user" role upon registration
- Immediately login after successful registration

### Requirements
- **No email verification** (as per requirements)
- **No admin approval** for basic user registration
- **Basic password policy**: Min 8 chars, 1 uppercase, 1 lowercase, 1 number
- **Rate limiting**: Prevent spam registrations
- **Works in both Docker and local development**

### Implementation Checklist
- [ ] Backend validation utility
- [ ] Keycloak admin client wrapper
- [ ] Registration API endpoint
- [ ] Rate limiting middleware
- [ ] Frontend validation utility
- [ ] Registration form component
- [ ] Updated routing and navigation
- [ ] Environment configuration
- [ ] Keycloak setup script updates
- [ ] Comprehensive testing
- [ ] Documentation updates

---

## Architecture

### Flow Diagram

```
┌─────────────┐
│   Browser   │
│  (React)    │
└──────┬──────┘
       │ 1. POST /auth/register
       │    {username, email, password, ...}
       ▼
┌─────────────────────────────────────────┐
│     Flask Auth Service                  │
│  ┌────────────────────────────────┐    │
│  │ Validation Layer               │    │
│  │ - Username format check        │    │
│  │ - Email format check           │    │
│  │ - Password strength check      │    │
│  │ - Sanitization                 │    │
│  └─────────────┬──────────────────┘    │
│                │                        │
│  ┌─────────────▼──────────────────┐    │
│  │ Registration Endpoint          │    │
│  │ - Check duplicate user/email   │    │
│  │ - Create user in Keycloak      │    │
│  │ - Assign 'user' role           │    │
│  └─────────────┬──────────────────┘    │
└────────────────┼───────────────────────┘
                 │ 2. Create user
                 │    via Admin API
                 ▼
      ┌──────────────────────┐
      │   Keycloak Server    │
      │  - User created      │
      │  - Role assigned     │
      │  - Ready for login   │
      └──────────┬───────────┘
                 │ 3. Success response
                 ▼
           ┌─────────────┐
           │   Browser   │
           │ Redirect to │
           │   Login     │
           └─────────────┘
```

### Component Breakdown

#### Backend Components
1. **validators.py** - Input validation and sanitization
2. **keycloak_admin_client.py** - Keycloak user management wrapper
3. **auth.py** - Registration endpoint
4. **config.py** - Configuration settings
5. **Flask-Limiter** - Rate limiting middleware

#### Frontend Components
1. **validators.js** - Client-side validation
2. **authService.js** - API communication
3. **Register.jsx** - Registration form component
4. **App.jsx** - Routing configuration
5. **Login.jsx** - Navigation to registration

---

## Backend Implementation

### Step 1: Create Validation Utility

**File:** `auth-service/app/utils/validators.py`

**Purpose:** Validate and sanitize user input

**Key Functions:**

```python
def validate_username(username: str) -> Dict[str, any]:
    """
    Validate username format

    Rules:
    - 3-20 characters
    - Alphanumeric, underscore, and dash only
    - Must start with a letter or number

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    pass

def validate_email(email: str) -> Dict[str, any]:
    """
    Validate email format using RFC 5322 compliant regex

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    pass

def validate_password_strength(password: str, min_length: int = 8) -> Dict[str, any]:
    """
    Validate password strength

    Rules:
    - Minimum 8 characters (configurable)
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number

    Returns:
        {'valid': True/False, 'error': 'error message', 'strength': 'weak/medium/strong'}
    """
    pass

def validate_name(name: str, field_name: str = 'Name') -> Dict[str, any]:
    """
    Validate first/last name (optional fields)

    Rules:
    - 1-50 characters if provided
    - Letters, spaces, hyphens, and apostrophes only

    Returns:
        {'valid': True/False, 'error': 'error message'}
    """
    pass

def sanitize_input(text: str) -> str:
    """
    Basic sanitization to prevent XSS
    - Remove HTML tags
    - Remove null bytes
    - Trim whitespace
    """
    pass

def validate_registration_data(data: dict, min_password_length: int = 8) -> Dict[str, any]:
    """
    Validate complete registration data

    Returns:
        {
            'valid': True/False,
            'errors': {'field': 'error message', ...},
            'sanitized_data': {'username': '...', 'email': '...', ...}
        }
    """
    pass
```

**Implementation Notes:**
- Use Python's `re` module for regex validation
- Email regex should follow RFC 5322 basic pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Username regex: `^[a-zA-Z0-9][a-zA-Z0-9_-]*$`
- Sanitize by removing HTML tags: `re.sub(r'<[^>]*>', '', text)`
- Always return consistent dictionary structures for easy error handling

---

### Step 2: Create Keycloak Admin Client Wrapper

**File:** `auth-service/app/keycloak_admin_client.py`

**Purpose:** Manage user creation in Keycloak

**Implementation:**

```python
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError, KeycloakPostError
from app.config import Config


class KeycloakAdminClient:
    def __init__(self):
        """Initialize Keycloak Admin client"""
        self.admin = KeycloakAdmin(
            server_url=Config.KEYCLOAK_SERVER_URL,
            username=Config.KEYCLOAK_ADMIN or 'admin',
            password=Config.KEYCLOAK_ADMIN_PASSWORD or 'admin',
            realm_name=Config.KEYCLOAK_REALM,
            verify=True
        )

    def check_user_exists(self, username: str = None, email: str = None) -> dict:
        """
        Check if user with username or email already exists

        Args:
            username: Username to check
            email: Email to check

        Returns:
            {
                'exists': True/False,
                'field': 'username' or 'email',
                'message': 'Error message if exists'
            }
        """
        try:
            # Check username
            if username:
                users = self.admin.get_users({"username": username})
                if users:
                    return {
                        'exists': True,
                        'field': 'username',
                        'message': 'Username already exists'
                    }

            # Check email
            if email:
                users = self.admin.get_users({"email": email})
                if users:
                    return {
                        'exists': True,
                        'field': 'email',
                        'message': 'Email already registered'
                    }

            return {'exists': False}

        except Exception as e:
            return {
                'exists': False,
                'error': f'Error checking user: {str(e)}'
            }

    def create_user(self, username: str, email: str, password: str,
                    first_name: str = '', last_name: str = '') -> dict:
        """
        Create new user in Keycloak

        Args:
            username: Unique username
            email: User email
            password: User password
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            {
                'success': True/False,
                'user_id': 'keycloak-user-id' (if success),
                'error': 'error message' (if failure)
            }
        """
        try:
            user_payload = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": False,  # Set to False since we skip verification
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False  # User doesn't need to change password on first login
                }]
            }

            # Create user
            user_id = self.admin.create_user(payload=user_payload)

            return {
                'success': True,
                'user_id': user_id
            }

        except KeycloakPostError as e:
            return {
                'success': False,
                'error': f'Failed to create user: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def assign_default_role(self, user_id: str) -> dict:
        """
        Assign default 'user' role to newly registered user

        Args:
            user_id: Keycloak user ID

        Returns:
            {'success': True/False, 'error': 'message' (if failure)}
        """
        try:
            # Get the 'user' role
            available_roles = self.admin.get_realm_roles()
            user_role = next((role for role in available_roles if role['name'] == 'user'), None)

            if not user_role:
                return {
                    'success': False,
                    'error': 'Default user role not found in Keycloak'
                }

            # Assign role to user
            self.admin.assign_realm_roles(user_id=user_id, roles=[user_role])

            return {'success': True}

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to assign role: {str(e)}'
            }

    def register_user(self, username: str, email: str, password: str,
                     first_name: str = '', last_name: str = '') -> dict:
        """
        Complete registration flow: check existence, create user, assign role

        Returns:
            {
                'success': True/False,
                'user_id': 'id' (if success),
                'username': 'username' (if success),
                'email': 'email' (if success),
                'error': 'message' (if failure)
            }
        """
        # Check if user already exists
        exists = self.check_user_exists(username=username, email=email)
        if exists['exists']:
            return {
                'success': False,
                'error': exists['message'],
                'field': exists['field']
            }

        # Create user
        result = self.create_user(username, email, password, first_name, last_name)
        if not result['success']:
            return result

        user_id = result['user_id']

        # Assign default role
        role_result = self.assign_default_role(user_id)
        if not role_result['success']:
            # User created but role assignment failed - log warning
            print(f"Warning: User {username} created but role assignment failed: {role_result['error']}")

        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'email': email
        }
```

**Key Points:**
- Uses existing `python-keycloak==3.7.0` library
- Inherits admin credentials from Config
- Checks for duplicate username AND email separately
- Returns consistent error structures
- Assigns 'user' role automatically
- Set `emailVerified: False` since we skip email verification
- Set `temporary: False` for password (no forced reset)

---

### Step 3: Add Registration Endpoint

**File:** `auth-service/app/routes/auth.py`

**Add the following imports:**

```python
from app.keycloak_admin_client import KeycloakAdminClient
from app.utils.validators import validate_registration_data
```

**Add registration endpoint:**

```python
# Initialize admin client
keycloak_admin = KeycloakAdminClient()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint

    Request body:
        {
            "username": "string (required)",
            "email": "string (required)",
            "password": "string (required)",
            "firstName": "string (optional)",
            "lastName": "string (optional)"
        }

    Returns:
        201: Registration successful
        400: Validation error
        409: Username or email already exists
        500: Server error
    """
    # Check if registration is enabled
    if not Config.REGISTRATION_ENABLED:
        return jsonify({'error': 'Registration is currently disabled'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # Validate input data
    validation_result = validate_registration_data(data, Config.MIN_PASSWORD_LENGTH)

    if not validation_result['valid']:
        return jsonify({
            'error': 'Validation failed',
            'details': validation_result['errors']
        }), 400

    sanitized_data = validation_result['sanitized_data']

    # Register user in Keycloak
    result = keycloak_admin.register_user(
        username=sanitized_data['username'],
        email=sanitized_data['email'],
        password=sanitized_data['password'],
        first_name=sanitized_data.get('firstName', ''),
        last_name=sanitized_data.get('lastName', '')
    )

    if not result['success']:
        # Check if it's a duplicate user error
        if 'field' in result:
            return jsonify({
                'error': result['error'],
                'field': result['field']
            }), 409  # Conflict

        return jsonify({'error': result['error']}), 500

    # Return success response
    return jsonify({
        'message': 'Registration successful',
        'username': result['username'],
        'email': result['email']
    }), 201
```

**Testing the endpoint:**

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "firstName": "New",
    "lastName": "User"
  }'
```

---

### Step 4: Update Configuration

**File:** `auth-service/app/config.py`

**Add new configuration variables:**

```python
class Config:
    # Existing config...

    # Registration settings
    REGISTRATION_ENABLED = os.getenv('REGISTRATION_ENABLED', 'true').lower() == 'true'
    MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', '8'))

    # Keycloak Admin credentials (for user management)
    KEYCLOAK_ADMIN = os.getenv('KEYCLOAK_ADMIN', 'admin')
    KEYCLOAK_ADMIN_PASSWORD = os.getenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
```

**Environment Files:**

**`.env.docker` (add these lines):**

```bash
# Registration settings
REGISTRATION_ENABLED=true
MIN_PASSWORD_LENGTH=8

# Keycloak admin credentials (already exist, just verify)
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

**`auth-service/.env` (for local development):**

```bash
# Registration settings
REGISTRATION_ENABLED=true
MIN_PASSWORD_LENGTH=8

# Keycloak admin credentials
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

---

### Step 5: Add Rate Limiting

**Purpose:** Prevent spam registrations and abuse

**Update:** `auth-service/requirements.txt`

```
flask==3.0.0
flask-cors==4.0.0
python-keycloak==3.7.0
PyJWT==2.8.0
cryptography==41.0.7
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
flask-limiter==3.5.0
```

**File:** `auth-service/app/__init__.py`

**Add rate limiting to the app factory:**

```python
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config

# Initialize limiter globally
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)

    # Initialize rate limiter
    limiter.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.protected import protected_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)

    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    return app
```

**Update:** `auth-service/app/routes/auth.py`

**Add rate limiting to registration endpoint:**

```python
from app import limiter

# Add rate limit decorator to register endpoint
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per 15 minutes")  # Max 5 registrations per 15 minutes per IP
def register():
    # ... existing code ...
```

**Rate Limit Configuration:**
- Registration: 5 requests per 15 minutes per IP
- Global: 200 requests per day, 50 per hour per IP
- Storage: In-memory (for production, use Redis)

**Testing Rate Limit:**

```bash
# Try to register 6 times quickly - 6th attempt should fail
for i in {1..6}; do
  curl -X POST http://localhost:5000/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"user$i\",\"email\":\"user$i@example.com\",\"password\":\"Pass123$i\"}"
  echo ""
done
```

---

### Step 6: Update Keycloak Setup Scripts

**Purpose:** Ensure service account has permission to create users

**File:** `auth-service/scripts/setup_keycloak_docker.py`

**Add after client creation (around line 145):**

```python
def assign_client_roles(self, client_id_internal: str):
    """
    Assign necessary roles to service account for user management

    Args:
        client_id_internal: Internal Keycloak client ID
    """
    print("🔐 Configuring service account permissions")

    try:
        # Get service account user
        service_account_user = self.keycloak_admin.get_client_service_account_user(client_id_internal)

        if not service_account_user:
            print("⚠️  Warning: Service account not found")
            return

        service_account_user_id = service_account_user['id']

        # Get realm-management client
        realm_mgmt_client_id = self.keycloak_admin.get_client_id('realm-management')

        # Get required roles
        available_roles = self.keycloak_admin.get_client_roles(realm_mgmt_client_id)

        roles_to_assign = []
        required_role_names = ['manage-users', 'view-users', 'query-users']

        for role_name in required_role_names:
            role = next((r for r in available_roles if r['name'] == role_name), None)
            if role:
                roles_to_assign.append(role)

        if roles_to_assign:
            # Assign client roles to service account
            self.keycloak_admin.assign_client_role(
                client_id=realm_mgmt_client_id,
                user_id=service_account_user_id,
                roles=roles_to_assign
            )
            print(f"✅ Assigned roles {[r['name'] for r in roles_to_assign]} to service account")
        else:
            print("⚠️  Warning: Required roles not found")

    except Exception as e:
        print(f"⚠️  Warning: Could not assign service account roles: {str(e)}")
        print("   You may need to manually assign 'manage-users' role in Keycloak admin console")
```

**Update `setup_all()` method to call this function:**

```python
def setup_all(self):
    """Run complete Keycloak setup"""
    # ... existing code ...

    # 2. Create client with predefined secret
    self.create_client_with_secret()

    # Get client ID for service account configuration
    client_id_internal = self.keycloak_admin.get_client_id(self.client_id)

    # 2.5 Configure service account permissions (NEW)
    self.assign_client_roles(client_id_internal)

    # 3. Create roles
    self.create_roles()

    # ... rest of existing code ...
```

**Do the same for:** `auth-service/scripts/setup_keycloak.py` (local development script)

---

## Frontend Implementation

### Step 1: Create Frontend Validation Utility

**File:** `frontend/src/utils/validators.js`

```javascript
/**
 * Frontend validation utilities for registration
 * Mirrors backend validation for better UX
 */

export const validateUsername = (username) => {
  if (!username) {
    return { valid: false, error: 'Username is required' };
  }

  if (username.length < 3) {
    return { valid: false, error: 'Username must be at least 3 characters' };
  }

  if (username.length > 20) {
    return { valid: false, error: 'Username must be no more than 20 characters' };
  }

  // Must start with letter or number, then alphanumeric, underscore, dash
  const usernamePattern = /^[a-zA-Z0-9][a-zA-Z0-9_-]*$/;
  if (!usernamePattern.test(username)) {
    return {
      valid: false,
      error: 'Username must start with a letter or number and contain only letters, numbers, underscores, and dashes'
    };
  }

  return { valid: true };
};

export const validateEmail = (email) => {
  if (!email) {
    return { valid: false, error: 'Email is required' };
  }

  // Basic RFC 5322 compliant email pattern
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }

  if (email.length > 255) {
    return { valid: false, error: 'Email is too long' };
  }

  return { valid: true };
};

export const validatePasswordStrength = (password, minLength = 8) => {
  if (!password) {
    return { valid: false, error: 'Password is required', strength: 'none' };
  }

  if (password.length < minLength) {
    return {
      valid: false,
      error: `Password must be at least ${minLength} characters`,
      strength: 'weak'
    };
  }

  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);

  if (!hasUpper) {
    return {
      valid: false,
      error: 'Password must contain at least one uppercase letter',
      strength: 'weak'
    };
  }

  if (!hasLower) {
    return {
      valid: false,
      error: 'Password must contain at least one lowercase letter',
      strength: 'weak'
    };
  }

  if (!hasDigit) {
    return {
      valid: false,
      error: 'Password must contain at least one number',
      strength: 'weak'
    };
  }

  // Determine strength
  let strength = 'medium';
  if (password.length >= 12 && /[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    strength = 'strong';
  }

  return { valid: true, strength };
};

export const getPasswordStrengthColor = (strength) => {
  const colors = {
    none: '#ddd',
    weak: '#ff4444',
    medium: '#ffaa00',
    strong: '#00C851'
  };
  return colors[strength] || colors.none;
};

export const validateName = (name, fieldName = 'Name') => {
  if (!name) {
    // Names are optional
    return { valid: true };
  }

  if (name.length > 50) {
    return { valid: false, error: `${fieldName} must be no more than 50 characters` };
  }

  // Allow letters, spaces, hyphens, apostrophes
  const namePattern = /^[a-zA-Z\s'-]+$/;
  if (!namePattern.test(name)) {
    return {
      valid: false,
      error: `${fieldName} can only contain letters, spaces, hyphens, and apostrophes`
    };
  }

  return { valid: true };
};
```

---

### Step 2: Update Auth Service

**File:** `frontend/src/services/authService.js`

**Add register method:**

```javascript
const authService = {
  // ... existing methods (login, logout, etc.) ...

  register: async (userData) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle validation errors
        if (data.details) {
          throw new Error(JSON.stringify(data.details));
        }
        throw new Error(data.error || 'Registration failed');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  // ... rest of existing methods ...
};

export default authService;
```

---

### Step 3: Create Registration Component

**File:** `frontend/src/components/Register.jsx`

```javascript
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
```

---

### Step 4: Update App Routing

**File:** `frontend/src/App.jsx`

```javascript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';  // NEW IMPORT
import Dashboard from './components/Dashboard';
import PublicPage from './components/PublicPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Navigate to="/public" replace />} />
          <Route path="/public" element={<PublicPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />  {/* NEW ROUTE */}

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/public" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
```

---

### Step 5: Update Login Component

**File:** `frontend/src/components/Login.jsx`

**Add import:**

```javascript
import { useNavigate, Link, useLocation } from 'react-router-dom';
```

**Add success message handler after component declaration:**

```javascript
const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();  // NEW
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

  // ... existing handleSubmit code ...
```

**Add success message display after the error div and before the submit button:**

```javascript
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
```

**Add registration link after the form, before the hint div:**

```javascript
        </form>

        {/* Registration Link (NEW) */}
        <div style={styles.footer}>
          Don't have an account?{' '}
          <Link to="/register" style={styles.link}>
            Sign up here
          </Link>
        </div>

        <div style={styles.hint}>
          {/* existing test users hint */}
        </div>
```

**Add new styles:**

```javascript
const styles = {
  // ... existing styles ...

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
};
```

---

## Testing

### Backend Testing

**File:** `auth-service/tests/test_registration.py`

```python
import pytest
from app import create_app
from app.keycloak_admin_client import KeycloakAdminClient
import json


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def keycloak_admin():
    """Create Keycloak admin client"""
    return KeycloakAdminClient()


def test_registration_success(client):
    """Test successful user registration"""
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'newuser_test',
            'email': 'newuser_test@example.com',
            'password': 'SecurePass123',
            'firstName': 'New',
            'lastName': 'User'
        }),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Registration successful'
    assert data['username'] == 'newuser_test'
    assert data['email'] == 'newuser_test@example.com'


def test_registration_duplicate_username(client):
    """Test registration with duplicate username"""
    # First registration
    client.post('/auth/register',
        data=json.dumps({
            'username': 'duplicate_user',
            'email': 'first@example.com',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )

    # Second registration with same username
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'duplicate_user',
            'email': 'second@example.com',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )

    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'already exists' in data['error'].lower()
    assert data['field'] == 'username'


def test_registration_duplicate_email(client):
    """Test registration with duplicate email"""
    # First registration
    client.post('/auth/register',
        data=json.dumps({
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )

    # Second registration with same email
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )

    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'already' in data['error'].lower()
    assert data['field'] == 'email'


def test_registration_invalid_email(client):
    """Test registration with invalid email format"""
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'details' in data
    assert 'email' in data['details']


def test_registration_weak_password(client):
    """Test registration with weak password"""
    weak_passwords = [
        'short',  # Too short
        'nouppercase1',  # No uppercase
        'NOLOWERCASE1',  # No lowercase
        'NoNumbers',  # No digits
    ]

    for password in weak_passwords:
        response = client.post('/auth/register',
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'details' in data
        assert 'password' in data['details']


def test_registration_invalid_username(client):
    """Test registration with invalid username format"""
    invalid_usernames = [
        'ab',  # Too short
        'a' * 21,  # Too long
        '_startwithunscore',  # Starts with underscore
        'has spaces',  # Contains spaces
        'has@special',  # Invalid special char
    ]

    for username in invalid_usernames:
        response = client.post('/auth/register',
            data=json.dumps({
                'username': username,
                'email': 'test@example.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'details' in data
        assert 'username' in data['details']


def test_registration_missing_required_fields(client):
    """Test registration with missing required fields"""
    # Missing username
    response = client.post('/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400

    # Missing email
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'password': 'SecurePass123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400

    # Missing password
    response = client.post('/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_registration_and_login_flow(client):
    """Test complete registration and login flow"""
    # Register new user
    reg_response = client.post('/auth/register',
        data=json.dumps({
            'username': 'flowtest_user',
            'email': 'flowtest@example.com',
            'password': 'FlowTest123',
            'firstName': 'Flow',
            'lastName': 'Test'
        }),
        content_type='application/json'
    )

    assert reg_response.status_code == 201

    # Login with newly registered user
    login_response = client.post('/auth/login',
        data=json.dumps({
            'username': 'flowtest_user',
            'password': 'FlowTest123'
        }),
        content_type='application/json'
    )

    assert login_response.status_code == 200
    login_data = json.loads(login_response.data)
    assert 'access_token' in login_data
    assert login_data['user_info']['username'] == 'flowtest_user'
    assert 'user' in login_data['user_info']['roles']


def test_registration_role_assignment(client, keycloak_admin):
    """Test that new users automatically get 'user' role"""
    username = 'roletest_user'

    # Register user
    client.post('/auth/register',
        data=json.dumps({
            'username': username,
            'email': 'roletest@example.com',
            'password': 'RoleTest123'
        }),
        content_type='application/json'
    )

    # Verify user exists in Keycloak
    users = keycloak_admin.admin.get_users({"username": username})
    assert len(users) == 1

    user_id = users[0]['id']

    # Check assigned roles
    roles = keycloak_admin.admin.get_realm_roles_of_user(user_id)
    role_names = [role['name'] for role in roles]

    assert 'user' in role_names
```

**Run tests:**

```bash
cd auth-service
pytest tests/test_registration.py -v
```

---

### Manual Testing Checklist

#### Docker Environment

```bash
# 1. Start services
docker-compose down -v && docker-compose up --build

# 2. Wait for all services to be ready
docker-compose logs -f keycloak-init  # Wait for "SETUP COMPLETED"

# 3. Test registration endpoint
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manualtest1",
    "email": "manual1@example.com",
    "password": "TestPass123",
    "firstName": "Manual",
    "lastName": "Test"
  }'

# Expected: 201 Created with success message

# 4. Test duplicate username
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manualtest1",
    "email": "different@example.com",
    "password": "TestPass123"
  }'

# Expected: 409 Conflict - "Username already exists"

# 5. Test login with new user
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manualtest1",
    "password": "TestPass123"
  }'

# Expected: 200 OK with access_token

# 6. Verify in Keycloak Admin Console
# Open http://localhost:8080
# Login: admin/admin
# Navigate to: microservices-realm → Users
# Find: manualtest1
# Verify: Role 'user' is assigned
```

#### Frontend Testing

**Open browser:** http://localhost:3000

**Test Cases:**

1. **Navigation**
   - [ ] Click "Sign up here" link on login page → Navigates to /register

2. **Form Validation**
   - [ ] Try submitting empty form → Shows validation errors
   - [ ] Enter username "ab" → Shows "at least 3 characters"
   - [ ] Enter invalid email "test" → Shows "Invalid email format"
   - [ ] Enter password "weak" → Shows password strength errors
   - [ ] Enter mismatched passwords → Shows "Passwords do not match"

3. **Password Strength Indicator**
   - [ ] Type "weak" → Red bar (weak)
   - [ ] Type "Weak1234" → Orange bar (medium)
   - [ ] Type "Strong123!@#" → Green bar (strong)

4. **Successful Registration**
   - [ ] Fill all required fields with valid data
   - [ ] Click Register → Redirects to login page
   - [ ] See success message "Registration successful!"
   - [ ] Username pre-filled in login form

5. **Error Handling**
   - [ ] Register with existing username → Shows "Username already exists"
   - [ ] Register with existing email → Shows "Email already registered"

6. **Complete Flow**
   - [ ] Register new user
   - [ ] Login with new credentials
   - [ ] Access dashboard → Shows user info with "user" role

---

## Deployment

### Docker Deployment

**No changes needed!** The Docker setup already includes:
- Keycloak admin credentials in `.env.docker`
- Service account with necessary permissions
- All environment variables configured

**Just rebuild and restart:**

```bash
docker-compose down -v
docker-compose up --build
```

---

### Local Development

**Steps:**

1. **Install new dependency:**

```bash
cd auth-service
source venv/bin/activate
pip install flask-limiter==3.5.0
pip freeze > requirements.txt
```

2. **Update .env file:**

```bash
# Add to auth-service/.env
REGISTRATION_ENABLED=true
MIN_PASSWORD_LENGTH=8
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

3. **Run setup script to ensure service account has permissions:**

```bash
cd auth-service
./setup.sh
```

4. **Start services:**

```bash
# Terminal 1: Start Keycloak
cd auth-service
docker-compose up

# Terminal 2: Start Flask
source venv/bin/activate
python run.py

# Terminal 3: Start React
cd frontend
npm run dev
```

---

## Security Considerations

### Input Validation

- **Frontend AND Backend validation** - Never trust client-side validation alone
- **Sanitize all inputs** - Remove HTML tags, null bytes
- **Use parameterized queries** - Keycloak handles this internally
- **Regex patterns** - Strict validation for username, email, password

### Rate Limiting

- **Registration:** 5 attempts per 15 minutes per IP
- **Global:** 200 requests per day, 50 per hour
- **Production:** Use Redis for distributed rate limiting

### Password Security

- **Minimum 8 characters** - Configurable via environment
- **Complexity requirements** - Upper, lower, digit required
- **Stored securely** - Keycloak uses bcrypt hashing
- **Not logged** - Never log passwords in error messages

### Authentication Flow

- **No email verification** - Users can login immediately (as per requirements)
- **Auto-assign user role** - Security by default
- **Admin approval not required** - For basic "user" role only
- **Admin role requires elevation** - Must be assigned manually in Keycloak

### XSS Prevention

- **Input sanitization** - Remove HTML tags
- **React auto-escaping** - JSX automatically escapes values
- **Content-Type headers** - Always JSON, never HTML

### CSRF Protection

- **Not needed for stateless JWT** - No cookies used
- **CORS configured** - Only allow specific origins in production

---

## Troubleshooting

### Common Issues

#### 1. "Service account not found" error

**Cause:** Client not configured with service accounts enabled

**Fix:**
```python
# In setup_keycloak_docker.py, verify client payload has:
"serviceAccountsEnabled": True
```

#### 2. "manage-users role not found" error

**Cause:** Service account doesn't have permission to create users

**Fix:**
```bash
# Manually in Keycloak Admin Console:
# 1. Go to Clients → auth-service → Service Account Roles
# 2. Client Roles → realm-management
# 3. Assign: manage-users, view-users, query-users
```

#### 3. Rate limit errors in development

**Cause:** Too many registration attempts

**Fix:**
```bash
# Temporarily disable rate limiting in development
# In auth.py, comment out:
# @limiter.limit("5 per 15 minutes")
```

#### 4. "Registration is currently disabled" error

**Cause:** REGISTRATION_ENABLED=false in environment

**Fix:**
```bash
# Check .env or .env.docker
REGISTRATION_ENABLED=true
```

#### 5. Frontend 404 on /auth/register

**Cause:** Nginx not proxying /api/auth/* to backend

**Fix:**
```nginx
# In frontend/nginx.conf, verify:
location /api/ {
    proxy_pass http://auth-service:5000/;
}
```

---

## Next Steps (Future Enhancements)

1. **Email Verification**
   - Send verification email with token
   - Require email confirmation before login
   - Use Keycloak's built-in SMTP support

2. **CAPTCHA Integration**
   - Google reCAPTCHA v3
   - Prevent bot registrations
   - Add to frontend and validate on backend

3. **Redis for Rate Limiting**
   - Replace in-memory storage
   - Distributed rate limiting for multiple instances
   - Persistent across restarts

4. **Password Reset Flow**
   - Forgot password functionality
   - Email-based reset tokens
   - Secure token generation

5. **Social Login**
   - Google OAuth
   - GitHub OAuth
   - Configured via Keycloak Identity Providers

6. **Profile Management**
   - Edit user profile
   - Change password
   - Update email

7. **Admin Dashboard**
   - Manage users
   - Assign roles
   - View registration analytics

---

## Conclusion

This comprehensive guide provides everything needed to implement user registration in the Keycloak authentication service. Follow the steps sequentially, test thoroughly, and ensure all security measures are in place before deploying to production.

**Estimated Implementation Time:** 10-14 hours

**Key Success Metrics:**
- Users can self-register via frontend
- All validation rules enforced
- Duplicate checks working
- Rate limiting active
- Users can immediately login after registration
- All tests passing

For questions or issues, refer to the troubleshooting section or create an issue in the project repository.
