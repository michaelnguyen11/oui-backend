import json
import logging
import os
import time
from typing import Optional

import boto3
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from open_webui.models.users import UserModel
from open_webui.utils.auth import get_verified_user
from open_webui.utils.access_control import has_access
from open_webui.models.models import Models
from open_webui.utils.payload import apply_model_params_to_body_openai, apply_model_system_prompt_to_body
from open_webui.env import SRC_LOG_LEVELS, ENABLE_FORWARD_USER_INFO_HEADERS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["BEDROCK"])

router = APIRouter()

class BedrockConfig(BaseModel):
    region: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None

class BedrockChatMessage(BaseModel):
    role: str
    content: str

class BedrockChatCompletionForm(BaseModel):
    model: str
    messages: list[BedrockChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    stop: Optional[list[str]] = None
    stream: Optional[bool] = False

    model_config = ConfigDict(extra="allow")

def get_bedrock_client(config: BedrockConfig):
    session = boto3.Session(
        aws_access_key_id=config.access_key_id,
        aws_secret_access_key=config.secret_access_key,
        aws_session_token=config.session_token,
        region_name=config.region
    )
    return session.client('bedrock-runtime')

@router.get("/v1/models")
async def get_bedrock_models(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """List available Bedrock models"""
    try:
        config = BedrockConfig(
            region=os.getenv("AWS_REGION", "us-east-1"),
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        
        client = get_bedrock_client(config)
        response = client.list_foundation_models()
        
        models = [
            {
                "id": model["modelId"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "aws",
                "permission": model.get("permissions", []),
                "input_modalities": model.get("inputModalities", []),
                "output_modalities": model.get("outputModalities", [])
            }
            for model in response.get("modelSummaries", [])
        ]
        
        return {
            "data": models,
            "object": "list"
        }
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Bedrock models: {str(e)}"
        )

@router.post("/v1/chat/completions")
async def generate_bedrock_chat_completion(
    request: Request,
    form_data: dict,
    user: UserModel = Depends(get_verified_user)
):
    """Generate chat completion using Bedrock models"""
    try:
        completion_form = BedrockChatCompletionForm(**form_data)
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    payload = {**completion_form.model_dump(exclude_none=True)}
    
    model_id = completion_form.model
    model_info = Models.get_model_by_id(model_id)
    
    if model_info:
        if model_info.base_model_id:
            payload["model"] = model_info.base_model_id
        params = model_info.params.model_dump()
        if params:
            payload = apply_model_params_to_body_openai(params, payload)
            payload = apply_model_system_prompt_to_body(params, payload, None, user)
            
        if user.role == "user":
            if not (user.id == model_info.user_id or has_access(user.id, type="read", access_control=model_info.access_control)):
                raise HTTPException(
                    status_code=403,
                    detail="Model not found"
                )
    else:
        if user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Model not found"
            )

    try:
        config = BedrockConfig(
            region=os.getenv("AWS_REGION", "us-east-1"),
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        
        client = get_bedrock_client(config)
        
        # Convert OpenAI format to Bedrock format
        bedrock_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": payload.get("max_tokens", 4096),
            "temperature": payload.get("temperature", 0.7),
            "top_p": payload.get("top_p", 1.0),
            "stop_sequences": payload.get("stop", []),
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in payload["messages"]
            ]
        }
        
        response = client.invoke_model(
            modelId=payload["model"],
            body=json.dumps(bedrock_payload)
        )
        
        response_body = json.loads(response.get('body').read())
        
        # Convert Bedrock response to OpenAI format
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": payload["model"],
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_body.get("content", [{}])[0].get("text", "")
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # Bedrock doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate completion: {str(e)}"
        ) 