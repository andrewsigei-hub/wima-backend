#!/bin/bash

# WIMA Serenity Gardens Backend Setup Script
# This script automates the initial setup process

set -e  # Exit on any error

echo "🏨 WIMA Serenity Gardens - Backend Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if PostgreSQL is running
echo "Checking PostgreSQL..."
if pg_isready > /dev/null 2>&1; then
    print_success "PostgreSQL is running"
else
    print_error "PostgreSQL is not running. Please start it first:"
    echo "  brew services start postgresql@14"
    exit 1
fi

# Check if pipenv is installed
echo ""
echo "Checking pipenv..."
if command -v pipenv &> /dev/null; then
    print_success "pipenv is installed"
else
    print_error "pipenv is not installed. Installing..."
    pip install pipenv
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pipenv install
print_success "Dependencies installed"

# Check if .env exists
echo ""
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual credentials before continuing"
    echo ""
    echo "Press Enter when you've updated the .env file..."
    read
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source "$(pipenv --venv)/bin/activate"
print_success "Virtual environment activated"

# Create database
echo ""
echo "Creating database..."
DB_NAME="wima_serenity_dev"

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    print_warning "Database '$DB_NAME' already exists"
    echo "Do you want to drop and recreate it? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        dropdb "$DB_NAME" || true
        createdb "$DB_NAME"
        print_success "Database recreated"
    fi
else
    createdb "$DB_NAME"
    print_success "Database created"
fi

# Run migrations
echo ""
echo "Setting up database migrations..."

if [ ! -d "migrations" ]; then
    print_warning "Initializing migrations..."
    FLASK_APP=run.py pipenv run flask db init
    print_success "Migrations initialized"
fi

echo "Creating migration..."
FLASK_APP=run.py pipenv run flask db migrate -m "Initial migration"
print_success "Migration created"

echo "Applying migration..."
FLASK_APP=run.py pipenv run flask db upgrade
print_success "Migration applied"

# Seed database
echo ""
echo "Seeding database with room data..."
pipenv run python seed_data.py
print_success "Database seeded"

# Run a quick test
echo ""
echo "Testing API..."
pipenv run python run.py &
SERVER_PID=$!
sleep 3

HEALTH_CHECK=$(curl -s http://localhost:5000/api/health | grep -o "healthy" || echo "failed")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    print_success "API is running correctly"
else
    print_error "API health check failed"
fi

# Kill the test server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "========================================"
print_success "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Review your .env file and ensure all credentials are correct"
echo "  2. Start the development server:"
echo "     pipenv run python run.py"
echo "  3. Test the API at http://localhost:5000/api/health"
echo "  4. Check the README.md for API endpoint documentation"
echo ""
echo "Happy coding! 🚀"