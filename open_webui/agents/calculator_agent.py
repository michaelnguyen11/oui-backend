from typing import Dict, Any
from smolagents import Agent, AgentConfig, Tool, ToolConfig

def calculate(operation: str, numbers: list) -> float:
    """Perform basic mathematical operations on a list of numbers"""
    if not numbers:
        return 0
    
    if operation == "add":
        return sum(numbers)
    elif operation == "multiply":
        result = 1
        for num in numbers:
            result *= num
        return result
    elif operation == "average":
        return sum(numbers) / len(numbers)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

def create_calculator_agent() -> Agent:
    """Create a calculator agent with basic mathematical tools"""
    
    # Create calculator tool
    calculator_tool = Tool(
        config=ToolConfig(
            name="calculator",
            description="A tool that can perform basic mathematical operations",
            function=calculate,
            parameters={
                "operation": {
                    "type": "string",
                    "description": "The mathematical operation to perform (add, multiply, average)",
                    "enum": ["add", "multiply", "average"]
                },
                "numbers": {
                    "type": "array",
                    "description": "List of numbers to perform the operation on",
                    "items": {"type": "number"}
                }
            }
        )
    )

    # Create agent configuration
    agent_config = AgentConfig(
        name="calculator_agent",
        description="An agent that can perform basic mathematical calculations",
        model="gpt-3.5-turbo",  # You can change this to any model you have configured
        temperature=0.7,
        system_prompt="""You are a helpful calculator agent that can perform basic mathematical operations.
        When given a task, break it down into steps and use the calculator tool to perform the necessary calculations.
        Always explain your reasoning and show your work."""
    )

    # Create and return the agent
    return Agent(
        config=agent_config,
        tools=[calculator_tool]
    ) 