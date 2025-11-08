# Keycloak Auth Service

A complete Python authentication service using Keycloak for JWT-based authentication in a local development environment.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Keycloak:**
   ```bash
   docker-compose up -d
   ```

4. **Configure Keycloak:**
   - Open http://localhost:8080
   - Login: admin / admin
   - Follow the complete setup guide in `/docs/local-setup-guide.md`

5. **Update .env file:**
   - Replace `YOUR_CLIENT_SECRET_HERE` with the actual client secret from Keycloak

6. **Run the service:**
   ```bash
   python run.py
   ```

## 🌐 Service URLs

- **Keycloak Admin Console:** http://localhost:8080
- **Auth Service API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

## 🧪 Test the Service

### Manual Testing (cURL)

**Test health:**
```bash
curl http://localhost:5000/health
```

**Login as test user:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

**Test protected endpoint:**
```bash
# Replace with actual token from login response
curl -X GET http://localhost:5000/api/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Automated Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v
```

## 📋 Test Users

After setting up Keycloak, you can create these test users:

- **Regular User:** `testuser` / `password123` (role: user)
- **Admin User:** `adminuser` / `admin123` (roles: user, admin)

## 📁 Project Structure

```
auth-service/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── keycloak_client.py       # Keycloak integration
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   └── protected.py         # Protected test endpoints
│   └── utils/
│       ├── __init__.py
│       └── jwt_utils.py         # JWT validation utilities
│
├── data/
│   └── clients.json             # In-memory client store
│
├── tests/
│   ├── __init__.py
│   └── test_auth.py             # Automated tests
│
├── logs/                        # Application logs
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Keycloak container setup
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── setup.sh                     # Unix setup script
└── setup.bat                    # Windows setup script
```

## 🔧 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/login` | POST | No | User login |
| `/auth/refresh` | POST | No | Refresh token |
| `/auth/logout` | POST | No | Logout user |
| `/auth/validate` | POST | No | Validate token |
| `/auth/userinfo` | GET | Yes | Get user info |
| `/api/public` | GET | No | Public endpoint |
| `/api/protected` | GET | Yes | Protected endpoint |
| `/api/admin` | GET | Yes (admin) | Admin-only endpoint |
| `/api/user-data` | GET | Yes | User data endpoint |
| `/health` | GET | No | Health check |

## 📖 Complete Guide

For detailed setup instructions, configuration options, and troubleshooting, see:
- `/docs/local-setup-guide.md` - Complete implementation guide

## ⚠️ Important Notes

- **Client Secret:** You MUST update the `.env` file with the actual Keycloak client secret
- **Ports:** Default ports are 8080 (Keycloak) and 5000 (Auth Service)
- **Virtual Environment:** Always activate the virtual environment before running
- **Development Only:** This setup is for development/testing only

## 🛠️ Development

- Flask runs in debug mode by default
- All code follows the guide specifications
- Comprehensive error handling and logging
- JWT token validation with role-based access control

## 📝 Common Commands

```bash
# Start Keycloak
docker-compose up -d

# Stop Keycloak
docker-compose down

# Run auth service
python run.py

# Run tests
pytest tests/ -v

# Check logs
docker-compose logs -f keycloak
```