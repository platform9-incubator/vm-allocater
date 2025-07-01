import httpx

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, SubnetCreate, SubnetCreateList, SubnetUpdate, SubnetUpdateList, CloudEnvironment


router = APIRouter(prefix="/subnets", tags=["subnets"])


# List all subnets
@router.get("/", tags=["Networking - List all Subnets"])
async def list_subnets(
    region: RegionName,
    network_id: Optional[str] = None,
    cidr: Optional[str] = None,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """List all subnets with optional filtering"""
    # TODO: Show only user related subnets, not all subnets in the region
    # TODO: Store subnets metadata in local database MySQL or MongoDB
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/subnets"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }

    params = {}
    if network_id:
        params["network_id"] = network_id
    if cidr:
        params["cidr"] = cidr
    
    response = await client.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Create subnet
@router.post("/", tags=["Networking - Create Subnets"])
async def create_subnet(
    region: RegionName,
    subnet_data_list: SubnetCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Create a new subnets"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/subnets"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response_list = []
    for subnet_data in subnet_data_list.subnets:
        if not isinstance(subnet_data, SubnetCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid subnet data provided"
            )
        
        response = await client.post(
            url,
            json={"subnet": subnet_data.dict(exclude_none=True)},
            headers=headers
        )

        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        response_list.append(response.json())
    return response_list

# Get subnet details
@router.get("/{subnet_id}", tags=["Networking - Get Subnet"])
async def get_subnet(
    region: RegionName,
    subnet_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Get specific subnet details"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/subnets/{subnet_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# TODO: Update subnet with valid and proper fields as per docs
@router.put("/{subnet_id}", tags=["Networking - Update Subnets"])
async def update_subnet(
    region: RegionName,
    subnet_id: str,
    subnet_data: SubnetUpdate,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Update subnet attributes"""
    ## TODO: Handle for update list with list of subnets update objects

    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/subnets/{subnet_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.put(
        url,
        json={"subnet": subnet_data.dict(exclude_none=True)},
        headers=headers
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Delete subnet
@router.delete("/{subnet_id}", tags=["Networking - Delete Subnet"])
async def delete_subnet(
    region: RegionName,
    subnet_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Delete a subnet"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/subnets/{subnet_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.delete(url, headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"status": "success", "message": "Subnet deleted successfully"}
