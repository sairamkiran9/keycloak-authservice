@echo off
REM SSO Test Runner Script for Windows
REM Runs all SSO-related tests for both backend and frontend

setlocal enabledelayedexpansion

echo 🧪 Running SSO Test Suite
echo =========================

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo ❌ Please run this script from the project root directory
    exit /b 1
)

echo 📋 Test Plan:
echo   1. Backend SSO unit tests
echo   2. Backend SSO integration tests
echo   3. Frontend SSO component tests
echo   4. Frontend SSO E2E tests
echo.

REM Backend Tests
echo 🐍 Running Backend Tests
echo ------------------------

cd auth-service

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found, creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install test dependencies if needed
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing test dependencies...
    pip install pytest pytest-mock
)

REM Run SSO-specific tests
echo Running SSO unit tests...
python -m pytest tests/test_sso.py -v
if errorlevel 1 (
    echo ❌ SSO unit tests failed
    exit /b 1
)
echo ✅ SSO unit tests passed

echo Running SSO integration tests...
python -m pytest tests/test_sso_integration.py -v
if errorlevel 1 (
    echo ❌ SSO integration tests failed
    exit /b 1
)
echo ✅ SSO integration tests passed

REM Return to project root
cd ..

REM Frontend Tests
echo.
echo ⚛️  Running Frontend Tests
echo -------------------------

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  Node modules not found, installing...
    npm install
)

REM Install test dependencies
npm list @testing-library/react >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing test dependencies...
    npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
)

REM Run SSO component tests
echo Running SSO component tests...
npm run test -- --run src/components/__tests__/SSOButton.test.jsx
if errorlevel 1 (
    echo ❌ SSOButton component tests failed
    exit /b 1
)
echo ✅ SSOButton component tests passed

echo Running OAuth callback tests...
npm run test -- --run src/components/__tests__/OAuthCallback.test.jsx
if errorlevel 1 (
    echo ❌ OAuthCallback component tests failed
    exit /b 1
)
echo ✅ OAuthCallback component tests passed

echo Running Login SSO integration tests...
npm run test -- --run src/components/__tests__/Login.sso.test.jsx
if errorlevel 1 (
    echo ❌ Login SSO integration tests failed
    exit /b 1
)
echo ✅ Login SSO integration tests passed

echo Running E2E SSO tests...
npm run test -- --run src/__tests__/sso-e2e.test.js
if errorlevel 1 (
    echo ❌ E2E SSO tests failed
    exit /b 1
)
echo ✅ E2E SSO tests passed

REM Return to project root
cd ..

REM Summary
echo.
echo 🎉 Test Summary
echo ===============
echo ✅ All SSO tests passed successfully!
echo.
echo 📊 Test Coverage:
echo   ✅ Backend SSO endpoints
echo   ✅ OAuth callback handling
echo   ✅ SSO provider discovery
echo   ✅ Frontend SSO components
echo   ✅ End-to-end SSO flow
echo   ✅ Error handling scenarios
echo.
echo 🚀 Ready for deployment!

REM Optional: Run quick integration test with Docker
where docker-compose >nul 2>&1
if not errorlevel 1 (
    echo.
    echo 🐳 Optional: Test with Docker
    echo Run 'docker-compose up --build' to test the complete SSO flow
)

endlocal