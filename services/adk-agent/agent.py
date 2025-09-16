from google.adk.agents import Agent

root_agent = Agent(
    name="hello_agent",
    instruction="You are a friendly agent that says hello.",
    model="gemini-1.5-flash",
)
