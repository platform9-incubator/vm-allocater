import os
import httpx

from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import datetime, timezone
from dotenv import load_dotenv 

from config import API_BASE_URLS, get_async_client, get_token, update_token 
from models import CloudEnvironment, RegionName

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Try to load .env.local, fall back to .env
load_dotenv(dotenv_path=".env.local", override=True)
load_dotenv()  # fallback if needed

def is_token_valid(cached_token: dict) -> bool:
    """
    Check if cached token exists and is not expired.
    Handles ISO 8601 format with timezone (e.g., "2025-06-28T21:17:54.634Z")
    """
    if not cached_token or not cached_token.get("auth_token"):
        return False
    
    expires_str = cached_token.get("expires")
    if not expires_str:
        return False
    
    try:
        # Parse ISO format with timezone (Zulu/UTC)
        expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) < expires_at
    except (ValueError, TypeError):
        return False
    
async def get_auth_token(cloud_environment: CloudEnvironment = CloudEnvironment.OSPC, region: RegionName = RegionName.IAD, client: httpx.AsyncClient = Depends(get_async_client)):
    """
    Authenticate with Rackspace OSPC Cloud and get an auth token.
    """

    # 1. We cache initially for token
    cached_token = get_token(cloud_environment.value, region.value)
    
    # 2. Validate cached token with expires time field
    if is_token_valid(cached_token):
        print(f"Using cached token for {cloud_environment.value} in region {region.value}")
        return {
            "auth_token": cached_token["auth_token"],
            "expires": cached_token["expires"],
            "tenant_id": cached_token.get("tenant_id")
        }
    
    # 3. Get new token if cache is invalid
    try:
        url = f"{API_BASE_URLS[cloud_environment.value]['identity']}/tokens"
        payload = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": os.getenv("AUTH_TOKEN_USERNAME"), # Credentials internally leverages tenant
                    "apiKey": os.getenv("AUTH_TOKEN_APIKEY")
                }
            }
        }

        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to authenticate with Rackspace Cloud"
            )
        
        data = response.json()
        token = data["access"]["token"]["id"]
        expires = data["access"]["token"]["expires"]
        tenant_id = data["access"]["token"]["tenant"]["id"]
        
        output = {
            "auth_token": token,
            "expires": expires,
            "tenant_id": tenant_id
        }

        # 4. Update cache with new fresh token
        await update_token(cloud_environment.value, region.value, output)

        return output

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Failed to authenticate with Rackspace Cloud"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Malformed authentication response: {str(e)}"
        )
