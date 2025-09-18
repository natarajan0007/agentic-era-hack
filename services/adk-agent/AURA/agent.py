from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
from toolbox_core import ToolboxSyncClient

import asyncio
import os

# Use an environment variable for the toolbox URL, with a default for local development
TOOLBOX_URL = os.environ.get("TOOLBOX_URL", "http://127.0.0.1:5000")
toolbox_client = ToolboxSyncClient(TOOLBOX_URL)

# The prompt for the agent
prompt = '''
You are AURA, a helpful AI assistant for our IT Service Management (ITSM) system. Your primary role is to help users create tickets and answer questions about their existing tickets.

**Core Capabilities:**

*   **Ticket Creation:** You can create new tickets for users. You should ask for all the necessary information, such as title, description, priority, and category. You should not ask for a ticket ID, as it will be generated automatically.
*   **Ticket Inquiry:** You can answer questions about existing tickets. This includes checking the status, priority, and other details of a ticket.
*   **Knowledge Base:** You can search the knowledge base for articles that might help users resolve their issues without creating a ticket.

**Behavioral Guidelines:**

*   **Differentiate Read and Write:** Your primary function is to distinguish between read-only queries and write operations.
    *   **Read Operations:** If the user is asking a question about tickets, users, or knowledge base articles, you should use the read-only tools to get the information and answer the user. The read-only tools are `search_tickets`, `get_ticket_details`, `search_knowledge_articles`, and `get_user_details`.
    *   **Write Operations:** If the user wants to create a ticket, you should use the `create_ticket_http` tool. Gather all the necessary information from the user before calling the tool. Do not ask for a ticket ID.
*   **Be Polite and Helpful:** Always be polite and helpful to users.
*   **Ask for Clarification:** If a user's query is ambiguous, ask for clarification. For example, if a user says "My computer is broken," ask for more details about the problem.
*   **Stay in Context:** Your role is to assist with ITSM tasks. If a user asks a question that is outside of this scope, you should politely inform them that you cannot answer and state your role.
'''

# Define the agent at the top (module) level.
# This is what the ADK framework looks for when it imports your file.
root_agent = Agent(
    model='gemini-2.5-flash',
    name='AURA',
    description='A helpful AI assistant for IT Service Management.',
    instruction=prompt,
    tools=toolbox_client.load_toolset("my-toolset"),
)

# This main function is for local testing.
async def main():
    # The 'with' statement is good practice for testing to ensure the client is closed.
    with ToolboxSyncClient(TOOLBOX_URL) as test_client:
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        session = await session_service.create_session(
            state={}, app_name='AURA', user_id='123'
        )
        runner = Runner(
            app_name='AURA',
            agent=root_agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        queries = [
            "I need to create a ticket for a broken printer.",
            "What is the status of ticket INC-20240101-00001?",
            "Search for all open tickets assigned to me.",
            "How do I reset my password?",
        ]

        for query in queries:
            print(f"\n--- USER QUERY: {query} ---\n")
            content = types.Content(role='user', parts=[types.Part(text=query)])
            events = runner.run(session_id=session.id,
                                user_id='123', new_message=content)

            responses = (
                part.text
                for event in events
                for part in event.content.parts
                if part.text is not None
            )

            for text in responses:
                print(text)

# This block guards the test execution.
# It will ONLY run when you execute `python your_file_name.py`.
if __name__ == "__main__":
    asyncio.run(main())
