from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
from toolbox_core import ToolboxSyncClient

import asyncio
import os

# TODO(developer): replace this with your Google API key
# os.environ['GOOGLE_API_KEY'] = 'your-api-key'
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# --- FIX START ---

# 1. Initialize the toolbox client at the module level.
#    This makes it available for the agent definition below.
toolbox_client = ToolboxSyncClient("http://127.0.0.1:5000")

# 2. Define the agent at the top (module) level and name the variable 'root_agent'.
#    This is what the ADK framework looks for when it imports your file.
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
from toolbox_core import ToolboxSyncClient

import asyncio
import os

# TODO(developer): replace this with your Google API key
# os.environ['GOOGLE_API_KEY'] = 'your-api-key'
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# --- FIX START ---

# 1. Initialize the toolbox client at the module level.
#    This makes it available for the agent definition below.
toolbox_client = ToolboxSyncClient("http://127.0.0.1:5000")

# 2. Define the agent at the top (module) level and name the variable 'root_agent'.
#    This is what the ADK framework looks for when it imports your file.
prompt = '''
You are Mando, a helpful AI assistant specializing in processing and managing PDF documents. Your primary role is to help users query and understand the data extracted from their uploaded PDF documents.

**Core Capabilities:**

*   **Search and Retrieve:** You can search for documents by filename, user, or processing status. You can also retrieve detailed information about specific documents.
*   **Data Extraction and Querying:** You can access and query the extracted data from the documents. This includes information about project contributors, cell site details, and site summaries.
*   **Statistics:** You can provide statistics on document processing.

**Date and Time Handling:**

*   You must handle relative date queries from the user. When you receive terms like "yesterday," "last week," "last month," "last quarter," or "the last X days," you must calculate the start and end dates yourself.
*   **Use today's date, September 5, 2025, as the reference for all calculations.**
*   Do not ask the user to clarify these dates. Calculate them and then use the appropriate tool with the dates in `YYYY-MM-DD` format.
*   **Examples based on today's date (2025-09-05):**
    *   "last 5 days": `start_date: 2025-08-31`, `end_date: 2025-09-05`
    *   "last month" (August): `start_date: 2025-08-01`, `end_date: 2025-08-31`
    *   "last quarter" (Q2 2025): `start_date: 2025-04-01`, `end_date: 2025-06-30`

**Data Structure:**

The data extracted from the PDFs is structured in JSON format. Here are some of the key fields you can be asked about:

*   `document_summary`: A summary of the document, including site information, originating company, and project contributors.
*   `project_contributors`: A list of people and organizations that contributed to the project.
*   `cell_site_details`: Detailed information about cell sites.
*   `site_summary`: A summary of the site information.
*   `drawing_register_summary`: A list of drawings in the document.
*   `extracted_data`: This field contains a combination of all the extracted information. When a user asks a general question about the content of a document, you should look in this field.

**Output Format:**

*   All of your responses should be in Markdown format.
*   When you are asked to provide structured data (e.g., a list of project contributors), you should format the output as a JSON object within a Markdown code block.

**Behavioral Guidelines:**

*   **Stay in Context:** Your role is to assist with PDF document processing. If a user asks a question that is outside of this scope, you should politely inform them that you cannot answer and state your role. For example, you can say: "As Mando, my role is to assist with PDF document processing. I cannot answer questions about other topics."
*   **Ask for Clarification:** If a user's query is ambiguous or if you need more information to provide an accurate answer, you should ask follow-up questions. For example, if a user asks for "the latest document," you should ask them to clarify what they mean by "latest" (e.g., "Do you mean the most recently uploaded document or the one with the most recent date of issue?").
*   **Read-Only Access:** You have read-only access to the database. You cannot create, update, or delete any information. You can only retrieve data.

By following these guidelines, you will be a helpful and efficient assistant for our users.
'''

agent = Agent(
    model='gemini-2.0-flash-001',
    name='pdf_processing_agent',
    description='A helpful AI assistant for PDF document processing and management.',
    instruction=prompt,
    tools=toolbox_client.load_toolset("my-toolset"),
)

# --- FIX END ---


# This main function is now just for your local testing.
async def main():
    # The 'with' statement is good practice for testing to ensure the client is closed.
    # Note that the global `root_agent` uses a separate, long-lived client instance.
    with ToolboxSyncClient("http://127.0.0.1:5000") as test_client:
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        session = await session_service.create_session(
            state={}, app_name='pdf_processing_agent', user_id='123'
        )
        runner = Runner(
            app_name='pdf_processing_agent',
            # Use the global 'root_agent' for the runner
            agent=agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        queries = [
            "Show me the most recent 5 documents that have been uploaded.",
            "Find any documents with 'report' in the filename.",
            "What's the processing status of all documents?",
            "Search for any content containing 'budget' in the extracted data.",
            "Show me processing statistics for all extractions.",
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


# 3. This block now correctly guards the test execution.
#    It will ONLY run when you execute `python your_file_name.py`.
#    It will be SKIPPED when the ADK framework imports your file.
if __name__ == "__main__":
    asyncio.run(main())


agent = Agent(
    model='gemini-2.0-flash-001',
    name='pdf_processing_agent',
    description='A helpful AI assistant for PDF document processing and management.',
    instruction=prompt,
    tools=toolbox_client.load_toolset("my-toolset"),
)

# --- FIX END ---


# This main function is now just for your local testing.
async def main():
    # The 'with' statement is good practice for testing to ensure the client is closed.
    # Note that the global `root_agent` uses a separate, long-lived client instance.
    with ToolboxSyncClient("http://127.0.0.1:5000") as test_client:
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        session = await session_service.create_session(
            state={}, app_name='pdf_processing_agent', user_id='123'
        )
        runner = Runner(
            app_name='pdf_processing_agent',
            # Use the global 'root_agent' for the runner
            agent=agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        queries = [
            "Show me the most recent 5 documents that have been uploaded.",
            "Find any documents with 'report' in the filename.",
            "What's the processing status of all documents?",
            "Search for any content containing 'budget' in the extracted data.",
            "Show me processing statistics for all extractions.",
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


# 3. This block now correctly guards the test execution.
#    It will ONLY run when you execute `python your_file_name.py`.
#    It will be SKIPPED when the ADK framework imports your file.
if __name__ == "__main__":
    asyncio.run(main())