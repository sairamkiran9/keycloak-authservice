#!/bin/bash

################################################################################
# Keycloak Auth Service - Verification Script
#
# This script verifies that all services are running correctly and performs
# basic health checks.
#
# Usage: ./verify.sh
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "  ${GREEN}✓ PASS${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_error() {
    echo -e "  ${RED}✗ FAIL${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_warning() {
    echo -e "  ${YELLOW}⚠ WARN${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}ℹ INFO${NC} $1"
}

check_url() {
    local url=$1
    local expected_code=${2:-200}

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" -eq "$expected_code" ]; then
        return 0
    else
        return 1
    fi
}

check_json_response() {
    local url=$1
    local expected_key=$2

    response=$(curl -s "$url" 2>/dev/null)

    if echo "$response" | grep -q "\"$expected_key\""; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Main Verification Steps
################################################################################

print_header "🔍 Keycloak Auth Service - Health Check"

################################################################################
# Docker Checks
################################################################################

echo -e "${GREEN}[1/8]${NC} Checking Docker..."
echo ""

print_test "Docker daemon is running"
if docker info > /dev/null 2>&1; then
    print_success "Docker is running"
else
    print_error "Docker is not running"
fi

print_test "Keycloak container is running"
if docker ps --format '{{.Names}}' | grep -q '^keycloak$'; then
    print_success "Keycloak container is running"

    # Check container health
    health_status=$(docker inspect --format='{{.State.Health.Status}}' keycloak 2>/dev/null || echo "none")
    if [ "$health_status" == "healthy" ]; then
        print_info "Container health: healthy"
    elif [ "$health_status" == "none" ]; then
        print_warning "No health check configured"
    else
        print_warning "Container health: $health_status"
    fi
else
    print_error "Keycloak container is not running"
    print_info "Start with: cd auth-service && docker-compose up -d keycloak"
fi

echo ""

################################################################################
# Keycloak Checks
################################################################################

echo -e "${GREEN}[2/8]${NC} Checking Keycloak..."
echo ""

print_test "Keycloak is responding at http://localhost:8080"
if check_url "http://localhost:8080" 200; then
    print_success "Keycloak web interface is accessible"
else
    print_error "Keycloak is not responding"
fi

print_test "Keycloak health endpoint"
if check_url "http://localhost:8080/health/ready" 200; then
    print_success "Keycloak is healthy"
else
    print_error "Keycloak health check failed"
fi

print_test "Keycloak realm is accessible"
if check_url "http://localhost:8080/realms/microservices-realm" 200; then
    print_success "Realm 'microservices-realm' exists"
else
    print_error "Realm not found or Keycloak not configured"
    print_info "Run Keycloak setup: cd auth-service && source venv/bin/activate && python scripts/setup_keycloak.py"
fi

echo ""

################################################################################
# Backend Checks
################################################################################

echo -e "${GREEN}[3/8]${NC} Checking Backend Service..."
echo ""

print_test "Backend process is running"
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_success "Backend is running (PID: $BACKEND_PID)"
    else
        print_error "Backend process not found (stale PID file)"
    fi
else
    if pgrep -f "python.*run.py" > /dev/null; then
        print_warning "Backend is running but PID file missing"
    else
        print_error "Backend is not running"
        print_info "Start with: cd auth-service && source venv/bin/activate && python run.py"
    fi
fi

print_test "Backend is responding at http://localhost:5000"
if check_url "http://localhost:5000/health" 200; then
    print_success "Backend is accessible"
else
    print_error "Backend is not responding"
fi

print_test "Backend health endpoint returns correct response"
if check_json_response "http://localhost:5000/health" "status"; then
    health_response=$(curl -s "http://localhost:5000/health" 2>/dev/null)
    print_success "Health check: $health_response"
else
    print_error "Backend health check returned unexpected response"
fi

echo ""

################################################################################
# Frontend Checks
################################################################################

echo -e "${GREEN}[4/8]${NC} Checking Frontend Service..."
echo ""

print_test "Frontend process is running"
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_success "Frontend is running (PID: $FRONTEND_PID)"
    else
        print_error "Frontend process not found (stale PID file)"
    fi
else
    if pgrep -f "vite.*dev" > /dev/null; then
        print_warning "Frontend is running but PID file missing"
    else
        print_error "Frontend is not running"
        print_info "Start with: cd frontend && npm run dev"
    fi
fi

print_test "Frontend is responding at http://localhost:3000"
if check_url "http://localhost:3000" 200; then
    print_success "Frontend is accessible"
else
    print_error "Frontend is not responding"
fi

echo ""

################################################################################
# Environment Configuration Checks
################################################################################

echo -e "${GREEN}[5/8]${NC} Checking Configuration..."
echo ""

print_test "Backend .env file exists"
if [ -f "auth-service/.env" ]; then
    print_success "Backend environment file found"

    # Check for required variables
    if grep -q "KEYCLOAK_CLIENT_SECRET" "auth-service/.env"; then
        print_info "Client secret is configured"
    else
        print_warning "Client secret may not be configured"
    fi
else
    print_error "Backend .env file not found"
fi

print_test "Frontend .env file exists"
if [ -f "frontend/.env" ]; then
    print_success "Frontend environment file found"
else
    print_error "Frontend .env file not found"
fi

echo ""

################################################################################
# Authentication Flow Test
################################################################################

echo -e "${GREEN}[6/8]${NC} Testing Authentication Flow..."
echo ""

print_test "User login with testuser"
login_response=$(curl -s -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "password123"}' 2>/dev/null)

if echo "$login_response" | grep -q "access_token"; then
    print_success "Login successful - access token received"

    # Extract token for further tests
    ACCESS_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

    if [ ! -z "$ACCESS_TOKEN" ]; then
        print_test "Access protected endpoint"
        protected_response=$(curl -s -X GET http://localhost:5000/api/protected \
            -H "Authorization: Bearer $ACCESS_TOKEN" 2>/dev/null)

        if echo "$protected_response" | grep -q "message"; then
            print_success "Protected endpoint accessible with token"
        else
            print_error "Protected endpoint not accessible"
        fi
    fi
else
    print_error "Login failed"
    print_info "Response: $login_response"
fi

echo ""

################################################################################
# Dependency Checks
################################################################################

echo -e "${GREEN}[7/8]${NC} Checking Dependencies..."
echo ""

print_test "Python virtual environment"
if [ -d "auth-service/venv" ]; then
    print_success "Virtual environment exists"
else
    print_error "Virtual environment not found"
    print_info "Run: cd auth-service && python3 -m venv venv"
fi

print_test "Node modules"
if [ -d "frontend/node_modules" ]; then
    print_success "Node modules installed"
else
    print_error "Node modules not found"
    print_info "Run: cd frontend && npm install"
fi

echo ""

################################################################################
# Summary
################################################################################

echo -e "${GREEN}[8/8]${NC} Test Summary"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

print_header "📊 Results"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC} ($TESTS_PASSED/$TOTAL_TESTS)"
    echo ""
    echo "Your Keycloak Auth Service is fully operational! 🎉"
    echo ""
    echo -e "${GREEN}Access your application:${NC}"
    echo "  • Frontend:  http://localhost:3000"
    echo "  • Backend:   http://localhost:5000"
    echo "  • Keycloak:  http://localhost:8080"
    echo ""
    echo -e "${GREEN}Test Credentials:${NC}"
    echo "  • User:  testuser / password123"
    echo "  • Admin: adminuser / admin123"
else
    echo -e "${RED}❌ Some tests failed${NC} ($TESTS_PASSED passed, $TESTS_FAILED failed out of $TOTAL_TESTS)"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check if all services are running: docker ps, ps aux | grep python, ps aux | grep vite"
    echo "  2. View logs: tail -f logs/backend.log logs/frontend.log"
    echo "  3. Restart services: ./cleanup.sh && ./setup.sh"
    echo "  4. Check Docker logs: cd auth-service && docker-compose logs keycloak"
    echo ""
    exit 1
fi

echo ""
