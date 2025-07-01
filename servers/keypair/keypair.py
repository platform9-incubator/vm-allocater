import httpx

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, CloudEnvironment, KeyPairCreate, KeyPairImport, KeyPairResponse

router = APIRouter(prefix="/keypairs", tags=["Key Pair Management"])


@router.post("/")
@router.post("")
async def create_keypair(
    region: RegionName,
    keypair_data: KeyPairCreate = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Create a new SSH key pair
    Returns:
        - Generated private key (only returned once - store it securely)
        - Public key
        - Fingerprint
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/os-keypairs"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    payload = {
        "keypair": keypair_data.dict()
    }
    
    try:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create keypair: {response.text}"
            )
        return response.json()["keypair"]
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection error while creating keypair: {str(e)}"
        )

@router.post("/import")
async def import_keypair(
    region: RegionName,
    keypair_data: KeyPairImport = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Import an existing public key
    Requires:
        - Key pair name
        - SSH public key content
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/os-keypairs"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    payload = {
        "keypair": keypair_data.dict()
    }
    
    try:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to import keypair: {response.text}"
            )
        return response.json()["keypair"]
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection error while importing keypair: {str(e)}"
        )

@router.get("/", response_model=List[KeyPairResponse])
@router.get("")
async def list_keypairs(
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    List all key pairs for the account
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/os-keypairs"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return [kp["keypair"] for kp in response.json()["keypairs"]]
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to list keypairs: {e.response.text}"
        )

@router.delete("/{keypair_name}")
async def delete_keypair(
    keypair_name: str,
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Delete a key pair by name
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/os-keypairs/{keypair_name}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    try:
        response = await client.delete(url, headers=headers)
        if response.status_code != 202:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to delete keypair: {response.text}"
            )
        return {"status": "success", "message": "Keypair deletion initiated"}
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection error while deleting keypair: {str(e)}"
        )