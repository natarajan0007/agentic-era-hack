#!/bin/bash

# AIITOps API Testing Script
# This script tests all API endpoints in the AIITOps backend

# Base URL for the API
BASE_URL="http://localhost:8011/api/v1"

# Colors for output
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

# Function to print section headers
print_header() {
  echo -e "\n${YELLOW}=======================================${NC}"
  echo -e "${YELLOW}  $1${NC}"
  echo -e "${YELLOW}=======================================${NC}\n"
}

# Function to print test results
print_result() {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✓ $2${NC}"
  else
    echo -e "${RED}✗ $2 - Failed with status code: $1${NC}"
  fi
}

# Store auth token
TOKEN=""

# Create a temporary directory for storing response data
TMP_DIR="/tmp/aiitops_api_test"
mkdir -p "$TMP_DIR"

# ==========================================
# Authentication Tests
# ==========================================
print_header "Authentication Endpoints"

# Test login
echo "Testing /auth/login endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@gmail.com&password=password123" \
  -o "$TMP_DIR/login.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /auth/login"

# Extract token if login successful
if [ "$STATUS_CODE" -eq 200 ]; then
  TOKEN=$(cat "$TMP_DIR/login.json" | grep -o '"access_token":"[^"]*"' | cut -d '"' -f 4)
  echo "Token obtained successfully"
fi

# Test register
echo "Testing /auth/register endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "name": "New User", "password": "password123", "role": "END_USER"}' \
  -o "$TMP_DIR/register.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /auth/register"

# Test get current user
echo "Testing /auth/me endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/me.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /auth/me"

# Test refresh token
echo "Testing /auth/refresh endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/refresh" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/refresh.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /auth/refresh"

# Test logout
echo "Testing /auth/logout endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/logout.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /auth/logout"

# ==========================================
# User Endpoints
# ==========================================
print_header "User Endpoints"

# Test get users
echo "Testing /users endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/users.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /users"

# Test get user by ID (using ID 1 as example)
echo "Testing /users/1 endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/user_1.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /users/1"

# Test update user
echo "Testing PUT /users/me endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}' \
  -o "$TMP_DIR/update_user.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "PUT /users/me"

# Test get departments
echo "Testing /users/departments endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users/departments" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/departments.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /users/departments"

# ==========================================
# Ticket Endpoints
# ==========================================
print_header "Ticket Endpoints"

# Test create ticket
echo "Testing POST /tickets endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Ticket",
    "description": "This is a test ticket created by the API testing script",
    "priority": "medium",
    "category": "software",
    "department_id": 1
  }' \
  -o "$TMP_DIR/create_ticket.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /tickets"

# Extract ticket ID if creation successful
TICKET_ID=""
if [ "$STATUS_CODE" -eq 201 ]; then
  TICKET_ID=$(cat "$TMP_DIR/create_ticket.json" | grep -o '"id":"[^"]*"' | cut -d '"' -f 4)
  echo "Created ticket ID: $TICKET_ID"
fi

# Test get tickets
echo "Testing GET /tickets endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/tickets.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /tickets"

# Test get ticket by ID
if [ ! -z "$TICKET_ID" ]; then
  echo "Testing GET /tickets/$TICKET_ID endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/tickets/$TICKET_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -o "$TMP_DIR/ticket_by_id.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "GET /tickets/$TICKET_ID"

  # Test update ticket
  echo "Testing PUT /tickets/$TICKET_ID endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/tickets/$TICKET_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Updated Test Ticket",
      "status": "in-progress"
    }' \
    -o "$TMP_DIR/update_ticket.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "PUT /tickets/$TICKET_ID"

  # Test assign ticket
  echo "Testing POST /tickets/$TICKET_ID/assign endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/tickets/$TICKET_ID/assign" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"assignee_id": 2}' \
    -o "$TMP_DIR/assign_ticket.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "POST /tickets/$TICKET_ID/assign"

  # Test escalate ticket
  echo "Testing POST /tickets/$TICKET_ID/escalate endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/tickets/$TICKET_ID/escalate" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"reason": "Testing escalation"}' \
    -o "$TMP_DIR/escalate_ticket.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "POST /tickets/$TICKET_ID/escalate"

  # Test analyze ticket
  echo "Testing POST /tickets/$TICKET_ID/analyze endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/tickets/$TICKET_ID/analyze" \
    -H "Authorization: Bearer $TOKEN" \
    -o "$TMP_DIR/analyze_ticket.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "POST /tickets/$TICKET_ID/analyze"
fi

# Test ticket stats
echo "Testing GET /tickets/stats/overview endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/tickets/stats/overview" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/ticket_stats.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /tickets/stats/overview"

# ==========================================
# Chat Endpoints
# ==========================================
print_header "Chat Endpoints"

# Test send message (if we have a ticket ID)
if [ ! -z "$TICKET_ID" ]; then
  echo "Testing POST /chat endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/chat" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "ticket_id": "'$TICKET_ID'",
      "message": "This is a test message",
      "message_type": "text",
      "is_internal": false
    }' \
    -o "$TMP_DIR/send_message.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "POST /chat"

  # Test get chat history
  echo "Testing GET /chat/$TICKET_ID/history endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/chat/$TICKET_ID/history" \
    -H "Authorization: Bearer $TOKEN" \
    -o "$TMP_DIR/chat_history.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "GET /chat/$TICKET_ID/history"

  # Test AI chat
  echo "Testing POST /chat/$TICKET_ID/ai-chat endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/chat/$TICKET_ID/ai-chat" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message": "How can I resolve this issue?"}' \
    -o "$TMP_DIR/ai_chat.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "POST /chat/$TICKET_ID/ai-chat"
fi

# ==========================================
# Knowledge Endpoints
# ==========================================
print_header "Knowledge Endpoints"

# Test get articles
echo "Testing GET /knowledge/articles endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/knowledge/articles" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/articles.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /knowledge/articles"

# Test create article
echo "Testing POST /knowledge/articles endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/knowledge/articles" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Knowledge Article",
    "content": "This is a test knowledge article created by the API testing script. It contains detailed information about testing.",
    "summary": "A test article for API testing",
    "category_id": 1,
    "status": "draft",
    "difficulty_level": "beginner",
    "estimated_read_time": 5,
    "tags": ["test", "api"]
  }' \
  -o "$TMP_DIR/create_article.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "POST /knowledge/articles"

# Extract article ID if creation successful
ARTICLE_ID=""
if [ "$STATUS_CODE" -eq 200 ] || [ "$STATUS_CODE" -eq 201 ]; then
  ARTICLE_ID=$(cat "$TMP_DIR/create_article.json" | grep -o '"id":[0-9]*' | head -1 | cut -d ':' -f 2)
  echo "Created article ID: $ARTICLE_ID"
fi

# Test get article by ID
if [ ! -z "$ARTICLE_ID" ]; then
  echo "Testing GET /knowledge/articles/$ARTICLE_ID endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/knowledge/articles/$ARTICLE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -o "$TMP_DIR/article_by_id.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "GET /knowledge/articles/$ARTICLE_ID"

  # Test update article
  echo "Testing PUT /knowledge/articles/$ARTICLE_ID endpoint..."
  RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/knowledge/articles/$ARTICLE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Updated Test Article",
      "status": "review"
    }' \
    -o "$TMP_DIR/update_article.json")

  STATUS_CODE=${RESPONSE: -3}
  print_result "$STATUS_CODE" "PUT /knowledge/articles/$ARTICLE_ID"
fi

# Test search knowledge
echo "Testing GET /knowledge/search endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/knowledge/search?query=test" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/knowledge_search.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /knowledge/search"

# Test get categories
echo "Testing GET /knowledge/categories endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/knowledge/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/categories.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /knowledge/categories"

# Test get tags
echo "Testing GET /knowledge/tags endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/knowledge/tags" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/tags.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /knowledge/tags"

# ==========================================
# Analytics Endpoints
# ==========================================
print_header "Analytics Endpoints"

# Test dashboard metrics
echo "Testing GET /analytics/dashboard endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/dashboard.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/dashboard"

# Test team performance
echo "Testing GET /analytics/team-performance endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/team-performance" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/team_performance.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/team-performance"

# Test SLA reports
echo "Testing GET /analytics/sla-reports endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/sla-reports" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/sla_reports.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/sla-reports"

# Test ticket analytics
echo "Testing GET /analytics/tickets endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/ticket_analytics.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/tickets"

# Test knowledge analytics
echo "Testing GET /analytics/knowledge endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/knowledge" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/knowledge_analytics.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/knowledge"

# Test system health
echo "Testing GET /analytics/system-health endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/analytics/system-health" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/system_health.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /analytics/system-health"

# ==========================================
# Transition Endpoints
# ==========================================
print_header "Transition Endpoints"

# Test get transition projects
echo "Testing GET /transition/projects endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/transition/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/transition_projects.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /transition/projects"

# Test get transition project by ID
echo "Testing GET /transition/projects/1 endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/transition/projects/1" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/transition_project_1.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /transition/projects/1"

# Test get knowledge artifacts
echo "Testing GET /transition/knowledge-artifacts endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/transition/knowledge-artifacts" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/knowledge_artifacts.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /transition/knowledge-artifacts"

# Test get team readiness
echo "Testing GET /transition/team-readiness endpoint..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/transition/team-readiness" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$TMP_DIR/team_readiness.json")

STATUS_CODE=${RESPONSE: -3}
print_result "$STATUS_CODE" "GET /transition/team-readiness"

# ==========================================
# Summary
# ==========================================
print_header "Test Summary"

echo "API testing completed. Results saved in $TMP_DIR"
echo "You can examine the JSON responses for each endpoint in that directory."

# Make the script executable
chmod +x "$0"