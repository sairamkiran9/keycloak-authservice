#!/bin/bash

################################################################################
# Keycloak Auth Service - Cleanup Script
#
# This script stops all services and optionally cleans up generated files
# and Docker containers/volumes for a fresh start.
#
# Usage: ./cleanup.sh [--full]
#   --full: Also remove Docker volumes and all generated files
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

# Check for --full flag
FULL_CLEANUP=false
if [ "$1" == "--full" ]; then
    FULL_CLEANUP=true
fi

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

################################################################################
# Main Cleanup Steps
################################################################################

print_header "🧹 Keycloak Auth Service - Cleanup"

################################################################################
# Step 1: Stop Backend Service
################################################################################

echo -e "${GREEN}[1/6]${NC} Stopping backend service..."

if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Backend service stopped (PID: $BACKEND_PID)"
    else
        print_info "Backend service was not running"
    fi
    rm -f logs/backend.pid
else
    print_info "No backend PID file found"
fi

# Kill any remaining Python processes running run.py
pkill -f "python.*run.py" 2>/dev/null && print_success "Killed remaining backend processes" || true

echo ""

################################################################################
# Step 2: Stop Frontend Service
################################################################################

echo -e "${GREEN}[2/6]${NC} Stopping frontend service..."

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend service stopped (PID: $FRONTEND_PID)"
    else
        print_info "Frontend service was not running"
    fi
    rm -f logs/frontend.pid
else
    print_info "No frontend PID file found"
fi

# Kill any remaining Vite processes
pkill -f "vite.*dev" 2>/dev/null && print_success "Killed remaining frontend processes" || true

echo ""

################################################################################
# Step 3: Stop Docker Containers
################################################################################

echo -e "${GREEN}[3/6]${NC} Stopping Docker containers..."

cd "$SCRIPT_DIR/auth-service"

if docker ps --format '{{.Names}}' | grep -q '^keycloak$'; then
    docker-compose stop keycloak
    print_success "Keycloak container stopped"
else
    print_info "Keycloak container was not running"
fi

# Check if we need to stop other containers from root docker-compose
cd "$SCRIPT_DIR"
if [ -f "docker-compose.yml" ]; then
    if docker ps --format '{{.Names}}' | grep -qE '^(auth-service|frontend)$'; then
        docker-compose stop 2>/dev/null || true
        print_success "Additional Docker containers stopped"
    fi
fi

echo ""

################################################################################
# Step 4: Remove Docker Containers (Optional)
################################################################################

echo -e "${GREEN}[4/6]${NC} Removing Docker containers..."

cd "$SCRIPT_DIR/auth-service"

if docker ps -a --format '{{.Names}}' | grep -q '^keycloak$'; then
    docker-compose down
    print_success "Keycloak container removed"
else
    print_info "No Keycloak container to remove"
fi

# Remove containers from root docker-compose
cd "$SCRIPT_DIR"
if [ -f "docker-compose.yml" ]; then
    docker-compose down 2>/dev/null || true
    print_success "Docker compose containers removed"
fi

echo ""

################################################################################
# Step 5: Full Cleanup (Optional)
################################################################################

if [ "$FULL_CLEANUP" = true ]; then
    echo -e "${GREEN}[5/6]${NC} Performing full cleanup..."

    # Remove Docker volumes
    print_info "Removing Docker volumes..."
    cd "$SCRIPT_DIR/auth-service"
    docker-compose down -v 2>/dev/null || true
    print_warning "Keycloak data volume removed (all Keycloak configuration lost)"

    cd "$SCRIPT_DIR"
    docker-compose down -v 2>/dev/null || true

    # Remove Python virtual environment
    if [ -d "auth-service/venv" ]; then
        print_info "Removing Python virtual environment..."
        rm -rf auth-service/venv
        print_success "Virtual environment removed"
    fi

    # Remove Node modules
    if [ -d "frontend/node_modules" ]; then
        print_info "Removing Node.js dependencies..."
        rm -rf frontend/node_modules
        print_success "Node modules removed"
    fi

    # Remove frontend build
    if [ -d "frontend/dist" ]; then
        rm -rf frontend/dist
        print_success "Frontend build removed"
    fi

    # Remove generated .env files
    print_info "Removing generated environment files..."
    rm -f auth-service/.env
    rm -f frontend/.env
    rm -f .env
    print_success "Environment files removed"

    # Remove client data
    if [ -d "auth-service/data" ]; then
        print_info "Removing client data..."
        rm -rf auth-service/data/*.json
        print_success "Client data removed"
    fi

    # Remove logs
    if [ -d "logs" ]; then
        print_info "Removing log files..."
        rm -rf logs/*
        print_success "Logs removed"
    fi

    # Remove auth-service logs
    if [ -d "auth-service/logs" ]; then
        rm -rf auth-service/logs/*.log
    fi

    echo ""
else
    echo -e "${GREEN}[5/6]${NC} Skipping full cleanup (use --full flag to remove all data)"
    print_info "Keeping:"
    print_info "  - Python virtual environment (auth-service/venv)"
    print_info "  - Node modules (frontend/node_modules)"
    print_info "  - Environment files (.env)"
    print_info "  - Keycloak data (Docker volume)"
    print_info "  - Client data (auth-service/data)"
    echo ""
fi

################################################################################
# Step 6: Cleanup Complete
################################################################################

echo -e "${GREEN}[6/6]${NC} ✅ Cleanup complete!"
echo ""

if [ "$FULL_CLEANUP" = true ]; then
    print_header "🎯 Full Cleanup Summary"
    echo -e "${YELLOW}All services stopped and data removed${NC}"
    echo ""
    echo "Removed:"
    echo "  ✓ All running services"
    echo "  ✓ Docker containers and volumes"
    echo "  ✓ Python virtual environment"
    echo "  ✓ Node.js dependencies"
    echo "  ✓ Environment files"
    echo "  ✓ Generated data and logs"
    echo ""
    echo -e "${GREEN}To set up again:${NC} ./setup.sh"
else
    print_header "🎯 Basic Cleanup Summary"
    echo -e "${YELLOW}Services stopped, data preserved${NC}"
    echo ""
    echo "Stopped:"
    echo "  ✓ Backend service"
    echo "  ✓ Frontend service"
    echo "  ✓ Docker containers"
    echo ""
    echo "Preserved:"
    echo "  ✓ Dependencies (venv, node_modules)"
    echo "  ✓ Environment configuration"
    echo "  ✓ Keycloak data"
    echo ""
    echo -e "${GREEN}To restart:${NC} ./setup.sh"
    echo -e "${GREEN}For full cleanup:${NC} ./cleanup.sh --full"
fi

echo ""
