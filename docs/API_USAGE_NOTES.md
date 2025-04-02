# API Usage Notes

## AWS Bedrock Integration

### Prerequisites
1. Enable Bedrock API in environment:
```bash
export ENABLE_BEDROCK_API=true
export AWS_REGION=us-east-1  # or your preferred region
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # optional
```

### Available Endpoints

#### 1. List Available Models
```bash
curl -X GET "http://localhost:3000/api/v1/bedrock/v1/models" \
     -H "Authorization: Bearer your_token"
```

Response:
```json
{
    "models": [
        {
            "id": "anthropic.claude-v2",
            "name": "Claude 2",
            "context_length": 100000,
            "input_cost_per_1k_tokens": 0.008,
            "output_cost_per_1k_tokens": 0.024
        },
        // ... other models
    ]
}
```

#### 2. Generate Chat Completion
```bash
curl -X POST "http://localhost:3000/api/v1/bedrock/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "model": "anthropic.claude-v2",
           "messages": [
             {
               "role": "user",
               "content": "What is the capital of France?"
             }
           ],
           "temperature": 0.7,
           "max_tokens": 100
         }'
```

Response:
```json
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1694268190,
    "model": "anthropic.claude-v2",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "The capital of France is Paris."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 7,
        "completion_tokens": 8,
        "total_tokens": 15
    }
}
```

## SmolAgents Integration

### Prerequisites
1. Enable SmolAgents in environment:
```bash
export ENABLE_SMOLAGENTS=true
export SMOLAGENTS_MAX_AGENTS=10
export SMOLAGENTS_MAX_TOOLS=20
export SMOLAGENTS_DEFAULT_MODEL=gpt-3.5-turbo
export SMOLAGENTS_DEFAULT_TEMPERATURE=0.7
```

### Available Endpoints

#### 1. Create a Tool
```bash
curl -X POST "http://localhost:3000/api/v1/smolagents/tools" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "name": "calculator",
           "description": "A simple calculator tool",
           "function": "calculate",
           "parameters": {
             "operation": {
               "type": "string",
               "description": "The mathematical operation to perform",
               "enum": ["add", "multiply", "average"]
             },
             "numbers": {
               "type": "array",
               "description": "List of numbers to perform the operation on",
               "items": {"type": "number"}
             }
           }
         }'
```

Response:
```json
{
    "id": "tool_0",
    "name": "calculator",
    "description": "A simple calculator tool",
    "function": "calculate",
    "parameters": {
        "operation": {
            "type": "string",
            "description": "The mathematical operation to perform",
            "enum": ["add", "multiply", "average"]
        },
        "numbers": {
            "type": "array",
            "description": "List of numbers to perform the operation on",
            "items": {"type": "number"}
        }
    }
}
```

#### 2. Create an Agent
```bash
curl -X POST "http://localhost:3000/api/v1/smolagents/agents" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "name": "math_agent",
           "description": "An agent that can perform mathematical calculations",
           "tools": ["tool_0"],
           "model": "gpt-3.5-turbo",
           "temperature": 0.7,
           "system_prompt": "You are a helpful calculator agent."
         }'
```

Response:
```json
{
    "id": "agent_0",
    "name": "math_agent",
    "description": "An agent that can perform mathematical calculations",
    "tools": ["tool_0"],
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "system_prompt": "You are a helpful calculator agent."
}
```

#### 3. List All Agents
```bash
curl -X GET "http://localhost:3000/api/v1/smolagents/agents" \
     -H "Authorization: Bearer your_token"
```

Response:
```json
[
    {
        "id": "agent_0",
        "name": "math_agent",
        "description": "An agent that can perform mathematical calculations",
        "tools": ["calculator"],
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "system_prompt": "You are a helpful calculator agent."
    }
]
```

#### 4. List All Tools
```bash
curl -X GET "http://localhost:3000/api/v1/smolagents/tools" \
     -H "Authorization: Bearer your_token"
```

Response:
```json
[
    {
        "id": "tool_0",
        "name": "calculator",
        "description": "A simple calculator tool",
        "function": "calculate",
        "parameters": {
            "operation": {
                "type": "string",
                "description": "The mathematical operation to perform",
                "enum": ["add", "multiply", "average"]
            },
            "numbers": {
                "type": "array",
                "description": "List of numbers to perform the operation on",
                "items": {"type": "number"}
            }
        }
    }
]
```

#### 5. Execute an Agent
```bash
curl -X POST "http://localhost:3000/api/v1/smolagents/agents/agent_0/execute" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "task": "Calculate the average of the numbers 10, 20, and 30",
           "context": {}
         }'
```

Response:
```json
{
    "result": "Let me help you calculate the average of those numbers.\n\nI'll use the calculator tool to find the average of 10, 20, and 30.\n\nUsing the calculator tool with operation 'average' and numbers [10, 20, 30]:\nThe average is 20.0",
    "agent_id": "agent_0",
    "task": "Calculate the average of the numbers 10, 20, and 30"
}
```

#### 6. Execute Calculator Agent (Pre-built)
```bash
curl -X POST "http://localhost:3000/api/v1/smolagents/calculator/execute" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "task": "Calculate the average of the numbers 10, 20, and 30",
           "context": {}
         }'
```

Response:
```json
{
    "result": "Let me help you calculate the average of those numbers.\n\nI'll use the calculator tool to find the average of 10, 20, and 30.\n\nUsing the calculator tool with operation 'average' and numbers [10, 20, 30]:\nThe average is 20.0",
    "task": "Calculate the average of the numbers 10, 20, and 30"
}
```

#### 7. Delete an Agent
```bash
curl -X DELETE "http://localhost:3000/api/v1/smolagents/agents/agent_0" \
     -H "Authorization: Bearer your_token"
```

Response:
```json
{
    "status": "success",
    "message": "Agent agent_0 deleted"
}
```

#### 8. Delete a Tool
```bash
curl -X DELETE "http://localhost:3000/api/v1/smolagents/tools/tool_0" \
     -H "Authorization: Bearer your_token"
```

Response:
```json
{
    "status": "success",
    "message": "Tool tool_0 deleted"
}
```

### Example Usage Flow

1. Create a tool:
```bash
# Create calculator tool
curl -X POST "http://localhost:3000/api/v1/smolagents/tools" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "name": "calculator",
           "description": "A simple calculator tool",
           "function": "calculate",
           "parameters": {
             "operation": {
               "type": "string",
               "description": "The mathematical operation to perform",
               "enum": ["add", "multiply", "average"]
             },
             "numbers": {
               "type": "array",
               "description": "List of numbers to perform the operation on",
               "items": {"type": "number"}
             }
           }
         }'
```

2. Create an agent with the tool:
```bash
# Create math agent with calculator tool
curl -X POST "http://localhost:3000/api/v1/smolagents/agents" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "name": "math_agent",
           "description": "An agent that can perform mathematical calculations",
           "tools": ["tool_0"],
           "model": "gpt-3.5-turbo",
           "temperature": 0.7
         }'
```

3. Execute the agent:
```bash
# Execute the agent with a task
curl -X POST "http://localhost:3000/api/v1/smolagents/agents/agent_0/execute" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_token" \
     -d '{
           "task": "Calculate the average of the numbers 10, 20, and 30",
           "context": {}
         }'
```

### Notes
1. All endpoints require authentication using a Bearer token
2. The calculator agent is pre-built and can be used directly without creating tools and agents
3. Tools and agents are stored in memory and will be lost when the server restarts
4. The system supports multiple agents and tools
5. Agents can use multiple tools
6. Tools can be shared between agents 