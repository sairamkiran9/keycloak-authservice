# Keycloak Auth Frontend

A React frontend for the Keycloak authentication service built with Vite.

## Features

- 🔐 **Authentication**: Login, logout, token refresh
- 🛡️ **Protected Routes**: Route guards for authenticated users
- 🔑 **Role-based Access**: Support for different user roles
- 📱 **Responsive Design**: Works on desktop and mobile
- ⚡ **Fast Development**: Vite for quick hot-reload development
- 🎯 **API Integration**: Full integration with auth service endpoints

## Quick Start

### Prerequisites

- Node.js 16+
- Auth service running on `http://localhost:5000`
- Keycloak running on `http://localhost:8080`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:3000

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:5000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx           # Login page
│   │   ├── Dashboard.jsx       # Protected dashboard
│   │   ├── PublicPage.jsx      # Public test page
│   │   └── ProtectedRoute.jsx  # Route guard
│   ├── context/
│   │   └── AuthContext.jsx     # Authentication state
│   ├── services/
│   │   └── authService.js      # API calls
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Styles
├── vite.config.js              # Vite configuration
├── package.json
└── .env                        # Environment variables
```

## Usage

### Test Users

After setting up Keycloak, use these test credentials:

| Username | Password | Roles |
|----------|----------|-------|
| testuser | password123 | user |
| adminuser | admin123 | user, admin |

### Testing Flow

1. **Public Page**: Visit http://localhost:3000/public
   - Test public API endpoint (no auth required)

2. **Login**: Click "Login" and enter credentials
   - Test user: `testuser` / `password123`
   - Admin user: `adminuser` / `admin123`

3. **Dashboard**: After successful login
   - View user information
   - Test protected endpoints
   - Test admin endpoint (admin user only)

4. **Logout**: Click "Logout" button
   - Should redirect to login page

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/login` | POST | No | User login |
| `/auth/refresh` | POST | No | Refresh token |
| `/auth/logout` | POST | No | Logout user |
| `/auth/userinfo` | GET | Yes | Get user info |
| `/api/public` | GET | No | Public endpoint |
| `/api/protected` | GET | Yes | Protected endpoint |
| `/api/admin` | GET | Yes (admin) | Admin endpoint |
| `/api/user-data` | GET | Yes | User data |

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Features in Detail

### Authentication Service (`src/services/authService.js`)

- **Token Management**: Automatic token storage and retrieval
- **Auto-refresh**: Automatic token refresh on API calls
- **Logout**: Proper token invalidation
- **Error Handling**: Comprehensive error handling

### Auth Context (`src/context/AuthContext.jsx`)

- **Global State**: User authentication state across the app
- **Login/Logout**: Centralized authentication methods
- **Loading States**: Loading indicators during auth operations

### Protected Routes (`src/components/ProtectedRoute.jsx`)

- **Route Guards**: Prevent unauthorized access
- **Redirect**: Automatic redirect to login if not authenticated
- **Loading State**: Show loading indicator during auth check

### Components

- **Login**: Clean login form with validation
- **Dashboard**: Protected dashboard with user info and API testing
- **PublicPage**: Public page for testing unauthenticated endpoints

## Development

### Vite Configuration

The Vite config includes proxy settings to avoid CORS issues:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': 'http://localhost:5000',
    '/auth': 'http://localhost:5000',
  }
}
```

### Adding New Features

1. **New Endpoints**: Add to `authService.js`
2. **New Components**: Add to `src/components/`
3. **New Routes**: Add to `App.jsx`
4. **State Management**: Extend `AuthContext.jsx`

## Troubleshooting

### CORS Errors
- Make sure Vite proxy is configured
- Verify auth service is running on port 5000

### Login Fails
- Check Keycloak is running on port 8080
- Verify test users exist in Keycloak
- Check network tab for detailed error messages

### Protected Routes Not Working
- Check localStorage for `access_token`
- Verify token is not expired
- Try logging out and back in

### Build Issues
```bash
# Clear build cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Next Steps

- Add unit tests with Vitest
- Implement form validation
- Add toast notifications
- Integrate UI library (Material-UI, Ant Design)
- Add internationalization (i18n)

## Dependencies

**Core:**
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `react-router-dom` ^6.8.0

**Development:**
- `@vitejs/plugin-react` ^4.0.3
- `vite` ^4.4.5
- `eslint` ^8.45.0

## License

MIT License