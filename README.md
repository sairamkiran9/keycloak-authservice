# Keycloak Auth Service + React Frontend

A complete authentication solution with **Keycloak** as the Identity Provider, **Python/Flask** auth service, and **React** frontend.

## 🌟 Features

- **🔐 Keycloak Integration**: Centralized authentication with JWT tokens
- **🐍 Python Auth Service**: Flask-based API gateway with role-based access control
- **⚛️ React Frontend**: Modern, responsive web application
- **🛡️ Security**: JWT validation, token refresh, protected routes
- **🚀 Quick Setup**: Automated scripts for instant development
- **📚 Comprehensive Docs**: Complete implementation guides

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React App     │    │  Auth Service    │    │   Keycloak      │
│   (Port 3000)   │◄──►│  (Port 5000)     │◄──►│  (Port 8080)    │
│                 │    │                  │    │                 │
│ • Login UI      │    │ • JWT Validation │    │ • User Auth     │
│ • Dashboard     │    │ • Token Refresh  │    │ • Token Issuer  │
│ • Protected     │    │ • Role Checking  │    │ • User Store    │
│   Routes        │    │ • API Gateway    │    │ • OAuth 2.0     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended - Fully Automated)

**One-command deployment with automatic Keycloak setup:**

```bash
docker-compose up --build
```

This will:
- ✅ Start Keycloak with default admin credentials (admin/admin)
- ✅ Automatically configure Keycloak (realm, client, users, roles)
- ✅ Start the Flask auth service
- ✅ Start the React frontend with Nginx
- ✅ Set up networking between all services

**Result**: Fully working application at http://localhost:3000 in ~2 minutes!

**Access points:**
- Frontend: http://localhost:3000
- Auth Service API: http://localhost:5000
- Keycloak Admin Console: http://localhost:8080 (admin/admin)

**Docker Commands:**
```bash
docker-compose up -d         # Start in background
docker-compose down          # Stop services
docker-compose down -v       # Stop and remove all data
docker-compose logs -f       # View logs
```

### ⚡ Local Development Setup (Complete End-to-End)

**Automated setup with Keycloak configuration, all dependencies, and service startup:**

```bash
./setup.sh
```

This script will:
- ✅ Check prerequisites (Docker, Python3, Node.js)
- ✅ Install backend dependencies (Python venv + packages)
- ✅ Install frontend dependencies (npm packages)
- ✅ Start Keycloak in Docker
- ✅ Automatically configure Keycloak (realm, client, users, roles)
- ✅ Generate all .env files with secrets
- ✅ Start backend and frontend services
- ✅ Verify everything is working
- ✅ Run authentication tests

**Result**: Fully working application at http://localhost:3000 in ~2 minutes!

**Additional Commands:**
```bash
./verify.sh          # Check health of all services
./cleanup.sh         # Stop all services
./cleanup.sh --full  # Stop services + remove all data
```

### Manual Setup

#### 1. Backend Setup (Keycloak + Auth Service)

```bash
# Navigate to auth service
cd auth-service

# Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start Keycloak
docker-compose up -d

# Configure Keycloak (see docs/local-setup-guide.md)
# Then update .env with client secret

# Start Auth Service
python run.py
```

#### 2. Frontend Setup (React App)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🌐 Service URLs

- **Frontend (React)**: http://localhost:3000
- **Auth Service (API)**: http://localhost:5000
- **Keycloak Admin**: http://localhost:8080 (admin/admin)

## 🧪 Test Users

After setting up Keycloak, create these test users:

| Username | Password | Roles |
|----------|----------|-------|
| testuser | password123 | user |
| adminuser | admin123 | user, admin |

## 📁 Project Structure

```
keycloak_authservice/
├── auth-service/              # Python/Flask backend
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── config.py          # Configuration
│   │   ├── keycloak_client.py # Keycloak integration
│   │   ├── routes/            # API endpoints
│   │   └── utils/             # JWT utilities
│   ├── scripts/
│   │   ├── setup_keycloak.py        # Local Keycloak setup
│   │   └── setup_keycloak_docker.py # Docker Keycloak setup
│   ├── data/                  # Client store
│   ├── tests/                 # Python tests
│   ├── Dockerfile             # Auth service container
│   ├── Dockerfile.init        # Keycloak init container
│   ├── requirements.txt       # Python deps
│   ├── .env                   # Local environment vars
│   └── run.py                 # Entry point
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── context/           # Auth context
│   │   ├── services/          # API service layer
│   │   ├── App.jsx            # Main app
│   │   └── main.jsx           # Entry point
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf             # Nginx config
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite config
│   └── .env                   # Local environment vars
│
├── docs/                      # Documentation
│   ├── local-setup-guide.md   # Complete setup guide
│   ├── REACT_FRONTEND_IMPLEMENTATION_GUIDE.md
│   └── ...
├── docker-compose.yml         # Complete Docker deployment
├── .env.docker                # Docker environment vars
├── setup.sh                   # Complete local setup
├── verify.sh                  # Health check script
├── cleanup.sh                 # Cleanup script
└── README.md                  # This file
```

## 🔧 API Endpoints

### Authentication (`/auth/*`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/login` | POST | No | User login |
| `/auth/refresh` | POST | No | Refresh token |
| `/auth/logout` | POST | No | Logout user |
| `/auth/validate` | POST | No | Validate token |
| `/auth/userinfo` | GET | Yes | Get user info |

### Protected API (`/api/*`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/public` | GET | No | Public endpoint |
| `/api/protected` | GET | Yes | Protected endpoint |
| `/api/admin` | GET | Yes (admin) | Admin endpoint |
| `/api/user-data` | GET | Yes | User data |

## 🛠️ Development

### Quick Commands

```bash
./setup.sh          # Complete setup (first time or reset)
./verify.sh         # Health check all services
./cleanup.sh        # Stop all services
./cleanup.sh --full # Stop + clean all data for fresh start
```

### Backend Development

```bash
cd auth-service
source venv/bin/activate
python run.py
```

- **Hot Reload**: Flask auto-reload enabled
- **Tests**: `pytest tests/ -v`
- **Keycloak**: `docker-compose logs -f keycloak`
- **Logs**: `tail -f ../logs/backend.log`

### Frontend Development

```bash
cd frontend
npm run dev
```

- **Hot Reload**: Vite HMR enabled
- **Proxy**: CORS handled via Vite proxy
- **Build**: `npm run build`
- **Logs**: `tail -f ../logs/frontend.log`

### Testing

#### Manual Testing (cURL)

```bash
# Test health
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Test protected endpoint
curl -X GET http://localhost:5000/api/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Automated Tests

```bash
# Backend tests
cd auth-service
pytest tests/ -v

# Frontend tests (optional)
cd frontend
npm test
```

## 📖 Documentation

### Complete Guides

- **[Docker Deployment Guide](guide/DOCKER_DEPLOYMENT_GUIDE.md)**: Complete Docker containerization with docker-compose
- **[Local Setup Guide](docs/local-setup-guide.md)**: Complete Keycloak + Auth Service setup
- **[React Implementation Guide](guide/REACT_FRONTEND_IMPLEMENTATION_GUIDE.md)**: Frontend development guide
- **[Keycloak Automation Guide](guide/KEYCLOAK_AUTOMATION_GUIDE.md)**: Automated Keycloak configuration

### Key Topics

- **Automated Setup**: One-command complete setup with `./setup.sh`
- **Keycloak Configuration**: Realm, clients, roles, users (automated)
- **JWT Token Flow**: Access/refresh token handling
- **Role-based Access**: User vs admin permissions
- **API Security**: Protected endpoints and validation
- **Frontend Integration**: React components and state management
- **Docker Deployment**: Containerized deployment with health checks

## 🔐 Security Features

### Backend Security

- **JWT Validation**: Signature and expiration checking
- **Token Refresh**: Automatic token renewal
- **Role-based Access**: Server-side permission checks
- **CORS Protection**: Configured for development
- **Input Validation**: Request data validation

### Frontend Security

- **Protected Routes**: Client-side route guards
- **Token Storage**: localStorage (consider httpOnly cookies for production)
- **Auto-logout**: On token expiration or 401 errors
- **HTTPS**: Required in production (use HTTP for dev only)

## 🚀 Deployment

### Docker Deployment (Recommended)

The project includes a complete Docker Compose setup with automated Keycloak configuration:

**Architecture:**
- **keycloak**: Identity provider (Keycloak 23.0)
- **keycloak-init**: One-time setup container that configures Keycloak
- **auth-service**: Flask backend API
- **frontend**: React app served by Nginx

**Key Features:**
- ✅ **Automated Setup**: Init container creates realm, client, users, and roles
- ✅ **Predefined Secrets**: Client secret configured via `.env.docker`
- ✅ **Service Dependencies**: Proper startup order with health checks
- ✅ **Persistent Data**: Keycloak data persists in Docker volumes
- ✅ **Networking**: Internal bridge network for service communication

**Configuration:**
- Environment variables: `.env.docker`
- Keycloak admin: admin/admin (change in production)
- Client secret: Predefined in `.env.docker` (change for production)
- Test users: testuser/password123, adminuser/admin123

**Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f keycloak-init  # View setup progress

# Restart specific service
docker-compose restart auth-service

# Full cleanup and rebuild
docker-compose down -v && docker-compose up --build
```

### Local Development

All services can run locally in development mode with hot reload:

```bash
./setup.sh    # One-time setup
./verify.sh   # Health checks
./cleanup.sh  # Stop services
```

### Production Considerations

1. **Environment Variables**: Use proper secrets management (not .env files)
2. **HTTPS**: Enable SSL/TLS for all services
3. **Database**: Replace JSON storage with proper database
4. **Token Storage**: Use httpOnly cookies instead of localStorage
5. **CORS**: Configure for production domains
6. **Rate Limiting**: Add API rate limiting
7. **Monitoring**: Add logging and monitoring
8. **Keycloak Admin**: Change default admin credentials
9. **Client Secret**: Generate strong random secret (not the example one)
10. **Init Container**: Consider using Keycloak imports instead for production

## 🐛 Troubleshooting

### Quick Fixes

**Docker Deployment:**
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f keycloak-init
docker-compose logs -f auth-service

# Full reset and rebuild
docker-compose down -v && docker-compose up --build

# Check service health
docker-compose ps
curl http://localhost:5000/health
```

**Local Development:**
```bash
# Check all services health
./verify.sh

# View service logs
tail -f logs/backend.log logs/frontend.log

# Full reset and restart
./cleanup.sh --full
./setup.sh
```

### Common Issues

#### Docker Issues

```bash
# Init container failing
docker-compose logs keycloak-init
# Common causes:
# - Keycloak not ready (should retry automatically)
# - Wrong credentials in .env.docker
# - Version mismatch in python-keycloak

# Services not starting
docker-compose ps  # Check status
docker-compose down -v  # Clean restart
docker-compose up --build

# Auth service can't connect to Keycloak
# Check network: docker network ls | grep keycloak
# Verify Keycloak is running: docker-compose ps keycloak
# Check .env.docker has correct KEYCLOAK_SERVER_URL=http://keycloak:8080

# Port conflicts
# If ports 3000, 5000, or 8080 are in use:
docker-compose down
# Kill processes using the ports, then:
docker-compose up

# Client secret mismatch
# Make sure .env.docker has the correct KEYCLOAK_CLIENT_SECRET
# If changed, rebuild: docker-compose down -v && docker-compose up --build
```

#### Setup Script Issues

```bash
# Permission denied
chmod +x setup.sh verify.sh cleanup.sh

# Prerequisites missing
# Install Docker, Python3, Node.js based on error messages

# Keycloak timeout
# Wait longer or check: docker logs keycloak
```

#### Backend Issues

```bash
# Keycloak not starting
cd auth-service
docker-compose down -v
docker-compose up -d

# Auth service not connecting
# Check .env file (automatically generated by setup.sh)
# Verify Keycloak is running: http://localhost:8080

# Backend not responding
tail -f logs/backend.log
```

#### Frontend Issues

```bash
# CORS errors (should be auto-fixed by setup.sh)
# If still occurring, check backend .env has flask-cors configured

# Build issues
cd frontend
rm -rf node_modules package-lock.json
npm install

# Frontend not starting
tail -f logs/frontend.log
```

#### Authentication Issues

```bash
# Login fails
./verify.sh  # Will test authentication

# Manual test
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

## 📈 Next Steps

1. **Add More Endpoints**: Extend API with application-specific routes
2. **Database Integration**: Replace JSON storage with PostgreSQL/MySQL
3. **UI Enhancement**: Add Material-UI, Ant Design, or custom styling
4. **Testing**: Add comprehensive unit and integration tests
5. **Monitoring**: Add logging, metrics, and health checks
6. **Documentation**: API documentation with Swagger/OpenAPI

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use descriptive commit messages

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check `/docs` folder
- **Issues**: Check troubleshooting section
- **Configuration**: Review environment variables and setup guides

---

**Built with ❤️ using Keycloak, Python/Flask, and React**