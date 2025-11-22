#!/bin/bash

# SSO Test Runner Script
# Runs all SSO-related tests for both backend and frontend

set -e

echo "🧪 Running SSO Test Suite"
echo "========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "📋 Test Plan:"
echo "  1. Backend SSO unit tests"
echo "  2. Backend SSO integration tests"
echo "  3. Frontend SSO component tests"
echo "  4. Frontend SSO E2E tests"
echo ""

# Backend Tests
echo "🐍 Running Backend Tests"
echo "------------------------"

cd auth-service

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Install test dependencies if needed
if ! pip show pytest > /dev/null 2>&1; then
    print_warning "Installing test dependencies..."
    pip install pytest pytest-mock
fi

# Run SSO-specific tests
echo "Running SSO unit tests..."
if python -m pytest tests/test_sso.py -v; then
    print_status "SSO unit tests passed"
else
    print_error "SSO unit tests failed"
    exit 1
fi

echo "Running SSO integration tests..."
if python -m pytest tests/test_sso_integration.py -v; then
    print_status "SSO integration tests passed"
else
    print_error "SSO integration tests failed"
    exit 1
fi

# Return to project root
cd ..

# Frontend Tests
echo ""
echo "⚛️  Running Frontend Tests"
echo "-------------------------"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found, installing..."
    npm install
fi

# Install test dependencies
if ! npm list @testing-library/react > /dev/null 2>&1; then
    print_warning "Installing test dependencies..."
    npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
fi

# Run SSO component tests
echo "Running SSO component tests..."
if npm run test -- --run src/components/__tests__/SSOButton.test.jsx; then
    print_status "SSOButton component tests passed"
else
    print_error "SSOButton component tests failed"
    exit 1
fi

echo "Running OAuth callback tests..."
if npm run test -- --run src/components/__tests__/OAuthCallback.test.jsx; then
    print_status "OAuthCallback component tests passed"
else
    print_error "OAuthCallback component tests failed"
    exit 1
fi

echo "Running Login SSO integration tests..."
if npm run test -- --run src/components/__tests__/Login.sso.test.jsx; then
    print_status "Login SSO integration tests passed"
else
    print_error "Login SSO integration tests failed"
    exit 1
fi

echo "Running E2E SSO tests..."
if npm run test -- --run src/__tests__/sso-e2e.test.js; then
    print_status "E2E SSO tests passed"
else
    print_error "E2E SSO tests failed"
    exit 1
fi

# Return to project root
cd ..

# Summary
echo ""
echo "🎉 Test Summary"
echo "==============="
print_status "All SSO tests passed successfully!"
echo ""
echo "📊 Test Coverage:"
echo "  ✅ Backend SSO endpoints"
echo "  ✅ OAuth callback handling"
echo "  ✅ SSO provider discovery"
echo "  ✅ Frontend SSO components"
echo "  ✅ End-to-end SSO flow"
echo "  ✅ Error handling scenarios"
echo ""
echo "🚀 Ready for deployment!"

# Optional: Run quick integration test with Docker
if command -v docker-compose > /dev/null 2>&1; then
    echo ""
    echo "🐳 Optional: Test with Docker"
    echo "Run 'docker-compose up --build' to test the complete SSO flow"
fi