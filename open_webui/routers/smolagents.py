import json
import logging
import os
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from smolagents import Agent, AgentConfig, Tool, ToolConfig

from open_webui.models.users import UserModel
from open_webui.utils.auth import get_verified_user
from open_webui.utils.access_control import has_access
from open_webui.models.models import Models
from open_webui.env import SRC_LOG_LEVELS
from open_webui.agents.calculator_agent import create_calculator_agent

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["SMOLAGENTS"])

router = APIRouter()

class AgentForm(BaseModel):
    name: str
    description: str
    tools: List[str]
    model: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None

    model_config = ConfigDict(extra="allow")

class ToolForm(BaseModel):
    name: str
    description: str
    function: str
    parameters: Dict[str, Any]

    model_config = ConfigDict(extra="allow")

class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    tools: List[str]
    model: str
    temperature: float
    max_tokens: Optional[int]
    system_prompt: Optional[str]

class ToolResponse(BaseModel):
    id: str
    name: str
    description: str
    function: str
    parameters: Dict[str, Any]

class AgentExecutionForm(BaseModel):
    agent_id: str
    task: str
    context: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

# In-memory storage for agents and tools
agents: Dict[str, Agent] = {}
tools: Dict[str, Tool] = {}

@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    request: Request,
    form_data: AgentForm,
    user: UserModel = Depends(get_verified_user)
):
    """Create a new agent"""
    try:
        # Get model info and verify access
        model_info = Models.get_model_by_id(form_data.model)
        if not model_info:
            raise HTTPException(status_code=404, detail="Model not found")
        
        if user.role == "user" and not (user.id == model_info.user_id or has_access(user.id, type="read", access_control=model_info.access_control)):
            raise HTTPException(status_code=403, detail="Model not found")

        # Create agent configuration
        config = AgentConfig(
            name=form_data.name,
            description=form_data.description,
            model=form_data.model,
            temperature=form_data.temperature,
            max_tokens=form_data.max_tokens,
            system_prompt=form_data.system_prompt
        )

        # Create agent with tools
        agent_tools = [tools[tool_id] for tool_id in form_data.tools if tool_id in tools]
        agent = Agent(config=config, tools=agent_tools)
        
        # Store agent
        agent_id = f"agent_{len(agents)}"
        agents[agent_id] = agent

        return {
            "id": agent_id,
            "name": agent.config.name,
            "description": agent.config.description,
            "tools": form_data.tools,
            "model": agent.config.model,
            "temperature": agent.config.temperature,
            "max_tokens": agent.config.max_tokens,
            "system_prompt": agent.config.system_prompt
        }

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.post("/tools", response_model=ToolResponse)
async def create_tool(
    request: Request,
    form_data: ToolForm,
    user: UserModel = Depends(get_verified_user)
):
    """Create a new tool"""
    try:
        # Create tool configuration
        config = ToolConfig(
            name=form_data.name,
            description=form_data.description,
            function=form_data.function,
            parameters=form_data.parameters
        )

        # Create tool
        tool = Tool(config=config)
        
        # Store tool
        tool_id = f"tool_{len(tools)}"
        tools[tool_id] = tool

        return {
            "id": tool_id,
            "name": tool.config.name,
            "description": tool.config.description,
            "function": tool.config.function,
            "parameters": tool.config.parameters
        }

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create tool: {str(e)}"
        )

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """List all agents"""
    try:
        return [
            {
                "id": agent_id,
                "name": agent.config.name,
                "description": agent.config.description,
                "tools": [tool.config.name for tool in agent.tools],
                "model": agent.config.model,
                "temperature": agent.config.temperature,
                "max_tokens": agent.config.max_tokens,
                "system_prompt": agent.config.system_prompt
            }
            for agent_id, agent in agents.items()
        ]
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}"
        )

@router.get("/tools", response_model=List[ToolResponse])
async def list_tools(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """List all tools"""
    try:
        return [
            {
                "id": tool_id,
                "name": tool.config.name,
                "description": tool.config.description,
                "function": tool.config.function,
                "parameters": tool.config.parameters
            }
            for tool_id, tool in tools.items()
        ]
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tools: {str(e)}"
        )

@router.post("/agents/{agent_id}/execute")
async def execute_agent(
    request: Request,
    agent_id: str,
    form_data: AgentExecutionForm,
    user: UserModel = Depends(get_verified_user)
):
    """Execute an agent with a given task"""
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = agents[agent_id]
        
        # Execute agent
        result = await agent.execute(
            task=form_data.task,
            context=form_data.context or {}
        )

        return {
            "result": result,
            "agent_id": agent_id,
            "task": form_data.task
        }

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute agent: {str(e)}"
        )

@router.delete("/agents/{agent_id}")
async def delete_agent(
    request: Request,
    agent_id: str,
    user: UserModel = Depends(get_verified_user)
):
    """Delete an agent"""
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        del agents[agent_id]
        return {"status": "success", "message": f"Agent {agent_id} deleted"}

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete agent: {str(e)}"
        )

@router.delete("/tools/{tool_id}")
async def delete_tool(
    request: Request,
    tool_id: str,
    user: UserModel = Depends(get_verified_user)
):
    """Delete a tool"""
    try:
        if tool_id not in tools:
            raise HTTPException(status_code=404, detail="Tool not found")

        # Remove tool from all agents
        for agent in agents.values():
            agent.tools = [tool for tool in agent.tools if tool.config.name != tools[tool_id].config.name]

        del tools[tool_id]
        return {"status": "success", "message": f"Tool {tool_id} deleted"}

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete tool: {str(e)}"
        )

@router.post("/calculator/execute")
async def execute_calculator_agent(
    request: Request,
    form_data: AgentExecutionForm,
    user: UserModel = Depends(get_verified_user)
):
    """Execute the calculator agent with a given task"""
    try:
        # Create calculator agent
        agent = create_calculator_agent()
        
        # Execute agent
        result = await agent.execute(
            task=form_data.task,
            context=form_data.context or {}
        )

        return {
            "result": result,
            "task": form_data.task
        }

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute calculator agent: {str(e)}"
        ) 