import httpx

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, PortCreate, PortCreateList, CloudEnvironment


router = APIRouter(prefix="/ports", tags=["ports"])


@router.post("/ports", tags=["Networking - Create Ports"])
async def create_port(
    region: RegionName,
    port_data_list: PortCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Create a new ports.
    # TODO: Assuming that at time of creation of server, network was created default by Rackspace and so no need to manually pass network field here
    # TODO: In future, provide option for creating a network here for users so that ports and all can be then created by users here as per convenience
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/ports"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response_list = []
    for port_data in port_data_list.ports:
        if not isinstance(port_data, PortCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid port data provided"
            )
        
        response = await client.post(url, json={"port": port_data.dict()}, headers=headers)
    
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        response_list.append(response)
        
    return response_list

@router.get("/ports", tags=["Networking - List Ports"])
async def list_ports(
    region: RegionName,
    device_id: Optional[str] = Query(None, description="Filter ports by device ID"),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    List all ports. Also handles device_id check here
    # TODO: Give ports wrt particular user only
    # TODO: Maybe store all ports metadata in local database MySQL or MongoDB
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/ports"

    if device_id:
        url = url+f"?device_id={device_id}"
    
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

@router.get("/{port_id}", tags=["Networking - Get Port"])
async def get_port(
    region: RegionName,
    port_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Get details of a specific port.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/ports/{port_id}"
    
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

# TODO: Needs to identify the fields that can be updated in a port
@router.put("/{port_id}", tags=["Networking - Update Port"])
async def update_port(
    region: RegionName,
    port_id: str,
    port_data: Dict[str, Any],
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Update a port's details.
    # TODO: Validate port_data fields based on OpenStack API documentation
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/ports/{port_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.put(url, json={"port": port_data}, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    
    return response.json()

@router.delete("/{port_id}", tags=["Networking - Delete Port"])
async def delete_port(
    region: RegionName,
    port_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Delete a port.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/ports/{port_id}"
    
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
    
    return {"status": "success", "message": "Port deleted successfully"}
