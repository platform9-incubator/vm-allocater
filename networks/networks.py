import httpx

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, NetworkCreate, NetworkCreateList, NetworkUpdate, NetworkUpdateList, CloudEnvironment


router = APIRouter(prefix="/networks", tags=["networks"])

# List all networks
@router.get("/", tags=["List Networks"])
async def list_networks(
    region: RegionName,
    name: Optional[str] = None,
    tenant_id: Optional[str] = None,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """List all networks with optional filtering"""
    # TODO: Show only user related networks, not all networks in the region
    # TODO: Store networks metadata in local database MySQL or MongoDB
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/networks"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    # Build query params
    params = {}
    if name:
        params["name"] = name
    if tenant_id:
        params["tenant_id"] = tenant_id
    
    response = await client.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Create network
@router.post("/{region}/networks", tags=["Create Networks"])
async def create_network(
    region: RegionName,
    network_data_list: NetworkCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Create a new network"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/networks"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response_list = []
    for network_data in network_data_list.networks:
        if not isinstance(network_data, NetworkCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid network data provided"
            )
        response = await client.post(
            url,
            json={"network": network_data.dict(exclude_none=True)},
            headers=headers
        )
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        response_list.append(response.json())
    return response_list

# Get network details
@router.get("/{network_id}", tags=["Get Network"])
async def get_network(
    region: RegionName,
    network_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Get specific network details"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/networks/{network_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Update network
# TODO: Update netwoks attributes to handle list of udpates
@router.put("/{network_id}", tags=["Update Networks"])
async def update_network(
    region: RegionName,
    network_id: str,
    network_data: NetworkUpdate,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Update network attributes"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/networks/{network_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.put(
        url,
        json={"network": network_data.dict(exclude_none=True)},
        headers=headers
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Delete network
@router.delete("/{network_id}", tags=["Delete Networks"])
async def delete_network(
    region: RegionName,
    network_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Delete a network"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/networks/{network_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.delete(url, headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"status": "success", "message": "Network deleted successfully"}
