#!/bin/bash

# API Testing Script for WIMA Serenity Gardens Backend
# Tests all major endpoints

BASE_URL="http://localhost:5000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧪 Testing WIMA Serenity Gardens API"
echo "===================================="
echo ""

# Function to print test header
test_header() {
    echo -e "${BLUE}Testing: $1${NC}"
}

# Function to print success
test_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo ""
}

# Function to pretty print JSON
pretty_json() {
    if command -v jq &> /dev/null; then
        echo "$1" | jq '.'
    else
        echo "$1"
    fi
}

# 1. Health Check
test_header "Health Check"
response=$(curl -s "${BASE_URL}/api/health")
pretty_json "$response"
test_success "Health check passed"

# 2. Get All Rooms
test_header "GET /api/rooms - Get all rooms"
response=$(curl -s "${BASE_URL}/api/rooms")
pretty_json "$response"
test_success "Retrieved all rooms"

# 3. Get Featured Rooms
test_header "GET /api/rooms/featured - Get featured rooms"
response=$(curl -s "${BASE_URL}/api/rooms/featured")
pretty_json "$response"
test_success "Retrieved featured rooms"

# 4. Get Single Room by Slug
test_header "GET /api/rooms/premier-room-1 - Get single room"
response=$(curl -s "${BASE_URL}/api/rooms/premier-room-1")
pretty_json "$response"
test_success "Retrieved single room"

# 5. Get Rooms by Type
test_header "GET /api/rooms/type/premier - Get rooms by type"
response=$(curl -s "${BASE_URL}/api/rooms/type/premier")
pretty_json "$response"
test_success "Retrieved rooms by type"

# 6. Submit Booking Inquiry
test_header "POST /api/inquiries - Submit booking inquiry"
response=$(curl -s -X POST "${BASE_URL}/api/inquiries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+254700000000",
    "inquiry_type": "booking",
    "room_id": 1,
    "check_in": "2026-03-15",
    "check_out": "2026-03-17",
    "guests": 2,
    "message": "This is a test booking inquiry."
  }')
pretty_json "$response"
test_success "Submitted booking inquiry"

# 7. Submit Event Inquiry
test_header "POST /api/inquiries/event - Submit event inquiry"
response=$(curl -s -X POST "${BASE_URL}/api/inquiries/event" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Event Planner",
    "email": "events@example.com",
    "phone": "+254700000000",
    "event_type": "wedding",
    "event_date": "2026-06-20",
    "guest_count": 150,
    "venue_preference": "field_1",
    "message": "This is a test event inquiry for a wedding."
  }')
pretty_json "$response"
test_success "Submitted event inquiry"

# 8. Submit Contact Form
test_header "POST /api/contact - Submit contact form"
response=$(curl -s -X POST "${BASE_URL}/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Contact",
    "email": "contact@example.com",
    "phone": "+254700000000",
    "subject": "General Inquiry",
    "message": "This is a test contact form message with more than 10 characters."
  }')
pretty_json "$response"
test_success "Submitted contact form"

# 9. Test Validation - Missing Fields
test_header "Validation Test - Missing required fields"
response=$(curl -s -X POST "${BASE_URL}/api/inquiries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User"
  }')
pretty_json "$response"
echo -e "${YELLOW}Expected error for missing fields${NC}"
echo ""

# 10. Test Validation - Invalid Email
test_header "Validation Test - Invalid email format"
response=$(curl -s -X POST "${BASE_URL}/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "invalid-email",
    "message": "This should fail validation"
  }')
pretty_json "$response"
echo -e "${YELLOW}Expected error for invalid email${NC}"
echo ""

# 11. Test 404 - Non-existent Room
test_header "404 Test - Non-existent room"
response=$(curl -s "${BASE_URL}/api/rooms/non-existent-room")
pretty_json "$response"
echo -e "${YELLOW}Expected 404 error${NC}"
echo ""

echo "===================================="
echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "Note: To see detailed responses, install jq:"
echo "  brew install jq"