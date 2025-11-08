#!/bin/bash

################################################################################
# Keycloak Auth Service - Complete Setup Script
#
# This script automates the complete setup of the Keycloak Authentication
# Service including:
#   - Prerequisite checks
#   - Backend dependency installation
#   - Frontend dependency installation
#   - Keycloak Docker container startup
#   - Automated Keycloak configuration (realm, client, users, roles)
#   - Environment file generation
#   - Service startup
#   - Health verification
#
# Usage: ./setup.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Global variables
KEYCLOAK_WAIT_TIME=90
BACKEND_PID=""
FRONTEND_PID=""

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

print_step() {
    echo -e "${GREEN}[$1/$2]${NC} $3"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

wait_for_url() {
    local url=$1
    local max_attempts=$2
    local attempt=1

    echo -ne "  ${YELLOW}⏳${NC} Waiting for service at $url..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f -o /dev/null "$url" 2>/dev/null; then
            echo -e "\r  ${GREEN}✓${NC} Service is ready!                                      "
            return 0
        fi
        echo -ne "\r  ${YELLOW}⏳${NC} Waiting... ($attempt/$max_attempts)  "
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "\r  ${RED}✗${NC} Timeout waiting for service                          "
    return 1
}

cleanup_on_error() {
    print_error "Setup failed! Cleaning up..."

    # Kill background processes if they exist
    if [ ! -z "$BACKEND_PID" ] && ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    exit 1
}

# Trap errors
trap cleanup_on_error ERR

################################################################################
# Main Setup Steps
################################################################################

print_header "🚀 Keycloak Auth Service - Complete Setup"

################################################################################
# Step 1: Check Prerequisites
################################################################################

print_step "1" "9" "Checking prerequisites..."

# Check Docker
if check_command docker; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | tr -d ',')
    print_success "Docker found (version $DOCKER_VERSION)"
else
    print_error "Docker not found"
    echo ""
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if check_command docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f4 | tr -d ',')
    print_success "Docker Compose found (version $COMPOSE_VERSION)"
elif docker compose version &> /dev/null; then
    print_success "Docker Compose found (Docker plugin)"
else
    print_error "Docker Compose not found"
    echo ""
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Python3
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f2)
    print_success "Python3 found (version $PYTHON_VERSION)"
else
    print_error "Python3 not found"
    echo ""
    echo "Please install Python3: https://www.python.org/downloads/"
    exit 1
fi

# Check pip3
if check_command pip3; then
    print_success "pip3 found"
else
    print_error "pip3 not found"
    echo ""
    echo "Please install pip3"
    exit 1
fi

# Check Node.js
if check_command node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found (version $NODE_VERSION)"
else
    print_error "Node.js not found"
    echo ""
    echo "Please install Node.js: https://nodejs.org/"
    exit 1
fi

# Check npm
if check_command npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm found (version $NPM_VERSION)"
else
    print_error "npm not found"
    echo ""
    echo "Please install npm (comes with Node.js)"
    exit 1
fi

echo ""

################################################################################
# Step 2: Backend Setup
################################################################################

print_step "2" "9" "Setting up backend..."

cd "$SCRIPT_DIR/auth-service"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_info "Installing Python dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Python dependencies installed"

cd "$SCRIPT_DIR"
echo ""

################################################################################
# Step 3: Frontend Setup
################################################################################

print_step "3" "9" "Setting up frontend..."

cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    print_info "Installing Node.js dependencies..."
    npm install --silent
    print_success "Node.js dependencies installed"
else
    print_info "Node.js dependencies already installed"
    print_warning "Run 'npm install' to update if needed"
fi

cd "$SCRIPT_DIR"
echo ""

################################################################################
# Step 4: Start Keycloak
################################################################################

print_step "4" "9" "Starting Keycloak..."

cd "$SCRIPT_DIR/auth-service"

# Check if Keycloak is already running
if docker ps --format '{{.Names}}' | grep -q '^keycloak$'; then
    print_info "Keycloak container is already running"
else
    print_info "Starting Keycloak container..."
    docker-compose up -d keycloak
    print_success "Keycloak container started"
fi

# Wait for Keycloak to be healthy
if wait_for_url "http://localhost:8080/" $KEYCLOAK_WAIT_TIME; then
    print_success "Keycloak is healthy and ready"
else
    print_error "Keycloak failed to become healthy"
    print_info "Check logs with: cd auth-service && docker-compose logs keycloak"
    exit 1
fi

cd "$SCRIPT_DIR"
echo ""

################################################################################
# Step 5: Configure Keycloak
################################################################################

print_step "5" "9" "Configuring Keycloak (realm, client, users, roles)..."

cd "$SCRIPT_DIR/auth-service"

# Run Keycloak setup script
print_info "Running Keycloak automation script..."
echo ""
source venv/bin/activate
python scripts/setup_keycloak.py

if [ $? -eq 0 ]; then
    print_success "Keycloak configured successfully"
else
    print_error "Keycloak configuration failed"
    exit 1
fi

cd "$SCRIPT_DIR"
echo ""

################################################################################
# Step 6: Environment Files Check
################################################################################

print_step "6" "9" "Verifying environment files..."

# Check if .env files were created
if [ -f "auth-service/.env" ]; then
    print_success "Backend .env file exists"
else
    print_error "Backend .env file not found"
    exit 1
fi

if [ -f "frontend/.env" ]; then
    print_success "Frontend .env file exists"
else
    print_error "Frontend .env file not found"
    exit 1
fi

echo ""

################################################################################
# Step 7: Start Services
################################################################################

print_step "7" "9" "Starting services..."

# Start backend
cd "$SCRIPT_DIR/auth-service"
print_info "Starting backend service..."
source venv/bin/activate
nohup python run.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 3

# Start frontend
cd "$SCRIPT_DIR/frontend"
print_info "Starting frontend service..."
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
print_success "Frontend started (PID: $FRONTEND_PID)"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Save PIDs to file for cleanup script
echo $BACKEND_PID > "$SCRIPT_DIR/logs/backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/logs/frontend.pid"

cd "$SCRIPT_DIR"
echo ""

################################################################################
# Step 8: Verify Setup
################################################################################

print_step "8" "9" "Verifying services..."

# Wait for backend
if wait_for_url "http://localhost:5000/health" 20; then
    print_success "Backend is running"
else
    print_error "Backend failed to start"
    print_info "Check logs: tail -f logs/backend.log"
    exit 1
fi

# Wait for frontend
if wait_for_url "http://localhost:3000" 20; then
    print_success "Frontend is running"
else
    print_error "Frontend failed to start"
    print_info "Check logs: tail -f logs/frontend.log"
    exit 1
fi

# Test authentication
print_info "Testing authentication..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "password123"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    print_success "Authentication test passed"
else
    print_warning "Authentication test failed (services may still be starting)"
fi

echo ""

################################################################################
# Step 9: Display Summary
################################################################################

print_step "9" "9" "✅ Setup Complete!"

print_header "📋 Service Information"

echo -e "${GREEN}Service URLs:${NC}"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:5000/health"
echo "  • Keycloak:  http://localhost:8080"
echo ""

echo -e "${GREEN}🔑 Test Credentials:${NC}"
echo "  • Regular User:  testuser / password123"
echo "  • Admin User:    adminuser / admin123"
echo "  • Keycloak Admin: admin / admin"
echo ""

echo -e "${GREEN}📝 Process Information:${NC}"
echo "  • Backend PID:  $BACKEND_PID"
echo "  • Frontend PID: $FRONTEND_PID"
echo "  • Logs: logs/backend.log, logs/frontend.log"
echo ""

echo -e "${GREEN}🛠 Useful Commands:${NC}"
echo "  • View backend logs:  tail -f logs/backend.log"
echo "  • View frontend logs: tail -f logs/frontend.log"
echo "  • View Keycloak logs: cd auth-service && docker-compose logs -f keycloak"
echo "  • Stop all services:  ./cleanup.sh"
echo "  • Verify services:    ./verify.sh"
echo ""

echo -e "${GREEN}📖 Next Steps:${NC}"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login with testuser / password123"
echo "  3. Explore the application"
echo "  4. Check guide/DOCKER_DEPLOYMENT_GUIDE.md for Docker deployment"
echo ""

print_header "🎉 All Done!"

echo -e "${YELLOW}Note:${NC} Services are running in the background."
echo -e "To stop all services, run: ${BLUE}./cleanup.sh${NC}"
echo ""
