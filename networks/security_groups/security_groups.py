import httpx

from fastapi import APIRouter, Depends, HTTPException, Body

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, SecurityGroupCreate, SecurityGroupCreateList, CloudEnvironment


router = APIRouter(prefix="/security_groups", tags=["security_groups"])

@router.post("/", tags=["Networking - Create Security Group"])
async def create_security_group(
    region: RegionName,
    group_data: SecurityGroupCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Create a new security group.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-groups"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }

    response_list = []
    for rule_data in group_data.security_groups:
        if not isinstance(rule_data, SecurityGroupCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid security group rules provided"
            )
        response = await client.post(url, json={"security_group": rule_data.dict()}, headers=headers)
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        response_list.append(response.json())
    return response_list

@router.get("/", tags=["Networking - List Security Groups"])
async def list_security_groups(
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    List all security groups.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-groups"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    
    return response.json()

@router.get("/{security_group_id}", tags=["Networking - Get Security Group"])
@router.get("")
async def get_security_group(
    region: RegionName,
    security_group_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Get details of a specific security group.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-groups/{security_group_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    
    return response.json()

@router.delete("/{security_group_id}", tags=["Networking - Delete Security Group"])
async def delete_security_group(
    region: RegionName,
    security_group_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Delete a security group.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-groups/{security_group_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.delete(url, headers=headers)
    
    if response.status_code != 204:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    
    return {"status": "success", "message": "Security group deleted successfully"}