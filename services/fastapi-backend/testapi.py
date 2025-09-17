#!/usr/bin/env python3

import requests
import json
import os
import tempfile
import inquirer
from colorama import Fore, Style, init
from typing import Optional, Dict, Any

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class APITester:
    def __init__(self):
        self.base_url = "http://localhost:8011/api/v1"
        self.token = ""
        self.tmp_dir = tempfile.mkdtemp(prefix="aiitops_api_test_")
        self.ticket_id = ""
        self.article_id = ""
        
    def print_header(self, title: str):
        """Print section headers with styling"""
        print(f"\n{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  {title}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")
        
    def print_result(self, status_code: int, endpoint: str):
        """Print test results with color coding"""
        if 200 <= status_code < 300:
            print(f"{Fore.GREEN}✓ {endpoint} - Status: {status_code}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {endpoint} - Failed with status code: {status_code}{Style.RESET_ALL}")
            
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request and return status code and response"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        default_headers = {}
        if self.token:
            default_headers["Authorization"] = f"Bearer {self.token}"
            
        if headers:
            default_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=default_headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=default_headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response.status_code, response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Request failed: {e}{Style.RESET_ALL}")
            return 0, {}
        except json.JSONDecodeError:
            return response.status_code, {}
            
    def test_authentication(self):
        """Test authentication endpoints"""
        self.print_header("Authentication Endpoints")
        
        # Test login
        print("Testing /auth/login endpoint...")
        login_data = {
            "username": "admin@gmail.com",
            "password": "password123"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # For form data, we need to handle it differently
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data="username=admin@gmail.com&password=password123",
                headers=headers
            )
            status_code = response.status_code
            self.print_result(status_code, "POST /auth/login")
            
            if status_code == 200:
                try:
                    token_data = response.json()
                    self.token = token_data.get("access_token", "")
                    if self.token:
                        print(f"{Fore.GREEN}Token obtained successfully{Style.RESET_ALL}")
                except:
                    print(f"{Fore.YELLOW}Login successful but couldn't extract token{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Login failed: {e}{Style.RESET_ALL}")
            
        # Test register
        print("Testing /auth/register endpoint...")
        register_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123",
            "role": "END_USER"
        }
        status_code, _ = self.make_request("POST", "/auth/register", register_data)
        self.print_result(status_code, "POST /auth/register")
        
        # Test get current user
        print("Testing /auth/me endpoint...")
        status_code, _ = self.make_request("GET", "/auth/me")
        self.print_result(status_code, "GET /auth/me")
        
        # Test refresh token
        print("Testing /auth/refresh endpoint...")
        status_code, _ = self.make_request("POST", "/auth/refresh")
        self.print_result(status_code, "POST /auth/refresh")
        
        # Test logout
        print("Testing /auth/logout endpoint...")
        status_code, _ = self.make_request("POST", "/auth/logout")
        self.print_result(status_code, "POST /auth/logout")
        
    def test_users(self):
        """Test user endpoints"""
        self.print_header("User Endpoints")
        
        # Test get users
        print("Testing /users endpoint...")
        status_code, _ = self.make_request("GET", "/users")
        self.print_result(status_code, "GET /users")
        
        # Test get user by ID
        print("Testing /users/1 endpoint...")
        status_code, _ = self.make_request("GET", "/users/1")
        self.print_result(status_code, "GET /users/1")
        
        # Test update user
        print("Testing PUT /users/me endpoint...")
        update_data = {"name": "Updated Name"}
        status_code, _ = self.make_request("PUT", "/users/me", update_data)
        self.print_result(status_code, "PUT /users/me")
        
        # Test get departments
        print("Testing /users/departments endpoint...")
        status_code, _ = self.make_request("GET", "/users/departments")
        self.print_result(status_code, "GET /users/departments")
        
    def test_tickets(self):
        """Test ticket endpoints"""
        self.print_header("Ticket Endpoints")
        
        # Test create ticket
        print("Testing POST /tickets endpoint...")
        ticket_data = {
            "title": "Test Ticket",
            "description": "This is a test ticket created by the API testing script",
            "priority": "medium",
            "category": "software",
            "department_id": 1
        }
        status_code, response = self.make_request("POST", "/tickets", ticket_data)
        self.print_result(status_code, "POST /tickets")
        
        if status_code == 201 and response:
            self.ticket_id = str(response.get("id", ""))
            if self.ticket_id:
                print(f"{Fore.GREEN}Created ticket ID: {self.ticket_id}{Style.RESET_ALL}")
                
        # Test get tickets
        print("Testing GET /tickets endpoint...")
        status_code, _ = self.make_request("GET", "/tickets")
        self.print_result(status_code, "GET /tickets")
        
        if self.ticket_id:
            # Test get ticket by ID
            print(f"Testing GET /tickets/{self.ticket_id} endpoint...")
            status_code, _ = self.make_request("GET", f"/tickets/{self.ticket_id}")
            self.print_result(status_code, f"GET /tickets/{self.ticket_id}")
            
            # Test update ticket
            print(f"Testing PUT /tickets/{self.ticket_id} endpoint...")
            update_data = {
                "title": "Updated Test Ticket",
                "status": "in-progress"
            }
            status_code, _ = self.make_request("PUT", f"/tickets/{self.ticket_id}", update_data)
            self.print_result(status_code, f"PUT /tickets/{self.ticket_id}")
            
            # Test assign ticket
            print(f"Testing POST /tickets/{self.ticket_id}/assign endpoint...")
            assign_data = {"assignee_id": 2}
            status_code, _ = self.make_request("POST", f"/tickets/{self.ticket_id}/assign", assign_data)
            self.print_result(status_code, f"POST /tickets/{self.ticket_id}/assign")
            
            # Test escalate ticket
            print(f"Testing POST /tickets/{self.ticket_id}/escalate endpoint...")
            escalate_data = {"reason": "Testing escalation"}
            status_code, _ = self.make_request("POST", f"/tickets/{self.ticket_id}/escalate", escalate_data)
            self.print_result(status_code, f"POST /tickets/{self.ticket_id}/escalate")
            
            # Test analyze ticket
            print(f"Testing POST /tickets/{self.ticket_id}/analyze endpoint...")
            status_code, _ = self.make_request("POST", f"/tickets/{self.ticket_id}/analyze")
            self.print_result(status_code, f"POST /tickets/{self.ticket_id}/analyze")
            
        # Test ticket stats
        print("Testing GET /tickets/stats/overview endpoint...")
        status_code, x = self.make_request("GET", "/tickets/stats/overview")
        print(x)
        self.print_result(status_code, "GET /tickets/stats/overview")
        
    def test_chat(self):
        """Test chat endpoints"""
        self.print_header("Chat Endpoints")
        
        if not self.ticket_id:
            print(f"{Fore.YELLOW}No ticket ID available. Creating a test ticket first...{Style.RESET_ALL}")
            # Create a quick ticket for chat testing
            ticket_data = {
                "title": "Chat Test Ticket",
                "description": "Ticket for testing chat functionality",
                "priority": "low",
                "category": "software",
                "department_id": 1
            }
            status_code, response = self.make_request("POST", "/tickets", ticket_data)
            if status_code == 201 and response:
                self.ticket_id = str(response.get("id", ""))
                
        if self.ticket_id:
            # Test send message
            print("Testing POST /chat endpoint...")
            message_data = {
                "ticket_id": self.ticket_id,
                "message": "This is a test message",
                "message_type": "text",
                "is_internal": False
            }
            status_code, _ = self.make_request("POST", "/chat", message_data)
            self.print_result(status_code, "POST /chat")
            
            # Test get chat history
            print(f"Testing GET /chat/{self.ticket_id}/history endpoint...")
            status_code, _ = self.make_request("GET", f"/chat/{self.ticket_id}/history")
            self.print_result(status_code, f"GET /chat/{self.ticket_id}/history")
            
            # Test AI chat
            print(f"Testing POST /chat/{self.ticket_id}/ai-chat endpoint...")
            ai_chat_data = {"message": "How can I resolve this issue?"}
            status_code, _ = self.make_request("POST", f"/chat/{self.ticket_id}/ai-chat", ai_chat_data)
            self.print_result(status_code, f"POST /chat/{self.ticket_id}/ai-chat")
        else:
            print(f"{Fore.RED}Cannot test chat endpoints without a valid ticket ID{Style.RESET_ALL}")
            
    def test_knowledge(self):
        """Test knowledge endpoints"""
        self.print_header("Knowledge Endpoints")
        
        # Test get articles
        print("Testing GET /knowledge/articles endpoint...")
        status_code, _ = self.make_request("GET", "/knowledge/articles")
        self.print_result(status_code, "GET /knowledge/articles")
        
        # Test create article
        print("Testing POST /knowledge/articles endpoint...")
        article_data = {
            "title": "Test Knowledge Article",
            "content": "This is a test knowledge article created by the API testing script. It contains detailed information about testing.",
            "summary": "A test article for API testing",
            "category_id": 1,
            "status": "draft",
            "difficulty_level": "beginner",
            "estimated_read_time": 5,
            "tags": ["test", "api"]
        }
        status_code, response = self.make_request("POST", "/knowledge/articles", article_data)
        self.print_result(status_code, "POST /knowledge/articles")
        
        if status_code in [200, 201] and response:
            self.article_id = str(response.get("id", ""))
            if self.article_id:
                print(f"{Fore.GREEN}Created article ID: {self.article_id}{Style.RESET_ALL}")
                
        if self.article_id:
            # Test get article by ID
            print(f"Testing GET /knowledge/articles/{self.article_id} endpoint...")
            status_code, _ = self.make_request("GET", f"/knowledge/articles/{self.article_id}")
            self.print_result(status_code, f"GET /knowledge/articles/{self.article_id}")
            
            # Test update article
            print(f"Testing PUT /knowledge/articles/{self.article_id} endpoint...")
            update_data = {
                "title": "Updated Test Article",
                "status": "review"
            }
            status_code, _ = self.make_request("PUT", f"/knowledge/articles/{self.article_id}", update_data)
            self.print_result(status_code, f"PUT /knowledge/articles/{self.article_id}")
            
        # Test search knowledge
        print("Testing GET /knowledge/search endpoint...")
        status_code, _ = self.make_request("GET", "/knowledge/search", params={"query": "test"})
        self.print_result(status_code, "GET /knowledge/search")
        
        # Test get categories
        print("Testing GET /knowledge/categories endpoint...")
        status_code, _ = self.make_request("GET", "/knowledge/categories")
        self.print_result(status_code, "GET /knowledge/categories")
        
        # Test get tags
        print("Testing GET /knowledge/tags endpoint...")
        status_code, _ = self.make_request("GET", "/knowledge/tags")
        self.print_result(status_code, "GET /knowledge/tags")
        
    def test_analytics(self):
        """Test analytics endpoints"""
        self.print_header("Analytics Endpoints")
        
        # Test dashboard metrics
        print("Testing GET /analytics/dashboard endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/dashboard")
        self.print_result(status_code, "GET /analytics/dashboard")
        
        # Test team performance
        print("Testing GET /analytics/team-performance endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/team-performance")
        self.print_result(status_code, "GET /analytics/team-performance")
        
        # Test SLA reports
        print("Testing GET /analytics/sla-reports endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/sla-reports")
        self.print_result(status_code, "GET /analytics/sla-reports")
        
        # Test ticket analytics
        print("Testing GET /analytics/tickets endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/tickets")
        self.print_result(status_code, "GET /analytics/tickets")
        
        # Test knowledge analytics
        print("Testing GET /analytics/knowledge endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/knowledge")
        self.print_result(status_code, "GET /analytics/knowledge")
        
        # Test system health
        print("Testing GET /analytics/system-health endpoint...")
        status_code, _ = self.make_request("GET", "/analytics/system-health")
        self.print_result(status_code, "GET /analytics/system-health")
        
    def test_transition(self):
        """Test transition endpoints"""
        self.print_header("Transition Endpoints")
        
        # Test get transition projects
        print("Testing GET /transition/projects endpoint...")
        status_code, _ = self.make_request("GET", "/transition/projects")
        self.print_result(status_code, "GET /transition/projects")
        
        # Test get transition project by ID
        print("Testing GET /transition/projects/1 endpoint...")
        status_code, _ = self.make_request("GET", "/transition/projects/1")
        self.print_result(status_code, "GET /transition/projects/1")
        
        # Test get knowledge artifacts
        print("Testing GET /transition/knowledge-artifacts endpoint...")
        status_code, _ = self.make_request("GET", "/transition/knowledge-artifacts")
        self.print_result(status_code, "GET /transition/knowledge-artifacts")
        
        # Test get team readiness
        print("Testing GET /transition/team-readiness endpoint...")
        status_code, _ = self.make_request("GET", "/transition/team-readiness")
        self.print_result(status_code, "GET /transition/team-readiness")
        
    def ensure_authentication(self):
        """Ensure user is authenticated before testing protected endpoints"""
        if not self.token:
            print(f"{Fore.YELLOW}🔐 Authentication required. Attempting to login...{Style.RESET_ALL}")
            self.perform_login()
            
    def perform_login(self):
        """Perform login to get authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data="username=admin@gmail.com&password=password123",
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    self.token = token_data.get("access_token", "")
                    if self.token:
                        print(f"{Fore.GREEN}✅ Login successful - Token obtained{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}❌ Login successful but no token received{Style.RESET_ALL}")
                        return False
                except:
                    print(f"{Fore.RED}❌ Login successful but couldn't parse response{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}❌ Login failed with status code: {response.status_code}{Style.RESET_ALL}")
                if response.text:
                    print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Login request failed: {e}{Style.RESET_ALL}")
            return False
            
    def run_interactive_menu(self):
        """Run the interactive menu for selecting endpoints to test"""
        print(f"{Fore.CYAN}🚀 AIITOps API Testing Tool{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Temporary directory: {self.tmp_dir}{Style.RESET_ALL}")
        
        # Protected endpoints that require authentication
        protected_endpoints = {
            "Users": self.test_users,
            "Tickets": self.test_tickets,
            "Chat": self.test_chat,
            "Knowledge": self.test_knowledge,
            "Analytics": self.test_analytics,
            "Transition": self.test_transition,
        }
        
        endpoint_categories = {
            "Authentication": self.test_authentication,
            **protected_endpoints,
            "All Endpoints": self.test_all_endpoints,
        }
        
        while True:
            questions = [
                inquirer.List(
                    'category',
                    message="Select endpoint category to test",
                    choices=list(endpoint_categories.keys()) + ["Exit"],
                    carousel=True
                ),
            ]
            
            answers = inquirer.prompt(questions)
            
            if not answers or answers['category'] == 'Exit':
                print(f"{Fore.YELLOW}Goodbye! 👋{Style.RESET_ALL}")
                break
                
            selected_category = answers['category']
            
            if selected_category in endpoint_categories:
                try:
                    # Check if this endpoint requires authentication
                    if selected_category in protected_endpoints:
                        self.ensure_authentication()
                        if not self.token:
                            print(f"{Fore.RED}❌ Cannot test {selected_category} - Authentication failed{Style.RESET_ALL}")
                            continue
                    
                    endpoint_categories[selected_category]()
                    print(f"\n{Fore.GREEN}✅ Testing completed for {selected_category}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Error testing {selected_category}: {e}{Style.RESET_ALL}")
                    
            # Ask if user wants to continue
            continue_questions = [
                inquirer.Confirm('continue', message="Do you want to test another category?", default=True),
            ]
            
            continue_answers = inquirer.prompt(continue_questions)
            if not continue_answers or not continue_answers['continue']:
                print(f"{Fore.YELLOW}Testing completed! Results saved in {self.tmp_dir}{Style.RESET_ALL}")
                break
                
    def test_all_endpoints(self):
        """Test all endpoints in sequence"""
        print(f"{Fore.CYAN}Testing all endpoints...{Style.RESET_ALL}")
        
        # Start with authentication
        self.test_authentication()
        
        # If authentication failed, ask if user wants to continue with other tests
        if not self.token:
            questions = [
                inquirer.Confirm('continue_without_auth', 
                               message="Authentication failed. Continue with other endpoint tests anyway?", 
                               default=False),
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or not answers['continue_without_auth']:
                print(f"{Fore.YELLOW}Skipping protected endpoints due to authentication failure{Style.RESET_ALL}")
                return
        
        # Test protected endpoints
        self.test_users()
        self.test_tickets()
        self.test_chat()
        self.test_knowledge()
        self.test_analytics()
        self.test_transition()

def main():
    """Main function to run the API tester"""
    try:
        tester = APITester()
        tester.run_interactive_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Testing interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()