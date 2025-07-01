import httpx
import time
import datetime

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Path

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, ServerCreate, ServerCreateList, CloudEnvironment, VolumeAttachmentCreate
from os_images import find_os_image_uuid_by_name
from flavors import flavor_id_mapping


router = APIRouter(prefix="/servers", tags=["servers"])


# Servers API Endpoints
@router.post("/", tags=["Create Servers"])
@router.post("")
async def create_server(
    region: RegionName,
    server_data_list: ServerCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Create new servers in the specified region.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response_list = []
    for server_data in server_data_list.servers:
        # Ensure the server data is a valid ServerCreate model
        if not isinstance(server_data, ServerCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid server data provided"
            )
        
        server_name = f"pooler-VM-{str(int(time.time()*1000))}"
        imageRef = find_os_image_uuid_by_name(server_data.imageRef)
        flavorRef = flavor_id_mapping.get(server_data.flavorRef, "general1-2")
        key_name = server_data.key_name if server_data.key_name else ""
        metadata = {
            "region": region.value,
            "cloud_environment": cloud_environment.value,
            "bid_price": "", # Integrate when auctioneer is attached as middleware
            "tenant_id": auth["tenant_id"],
            "server_name": server_data.name if server_data.name else server_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "key_name": key_name,
            # ""
            "image": server_data.imageRef, # Update with new idea later ( short name )
            # "flavor": flavorRef # Stores full flavor here -> Works for OSPC only for now, TODO: For Flex in future
            "flavor": flavorRef.split("-")[0][:-1] # Works for OSPC only for now, TODO: For Flex in future
        }

        final_server_data = {
            "name": server_name,
            "imageRef": imageRef,
            "flavorRef": flavorRef,
            "metadata": metadata,
            "key_name": key_name
        }
        print(f"\nFinal server data: {final_server_data}")
        # Convert to dict for JSON serialization
        response = await client.post(url, json={"server": final_server_data}, headers=headers)
        
        print(f"Response Status: {response.status_code} \n Data: {response.json()}")
        print(f"Creating server in {region} with data: {server_data.dict()}")
        if response.status_code not in [200, 201, 202]:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        print(f"\nServer created successfully in {region} with status code: {response.status_code} data: {response.json()}")
        response_list.append(response.json())
    return {"servers": response_list, "message": "Servers created successfully", "status_code": response.status_code}

@router.get("/", tags=["List Servers"])
async def list_servers(
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    List all servers in the specified region irrespective of user
    TODO: Modify it such that it gives all servers of particular user
    TODO: Maybe store all server metadata in local database MySQL or MongoDB
    """
    try:
        auth: dict = await get_auth_token(cloud_environment, region, client)

        base_url = API_BASE_URLS[cloud_environment.value]["servers"]
        url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers"
        
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
    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot connect to Rackspace API: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Rackspace API error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/{server_id}", tags=["Get Server"])
@router.get("")
async def get_server(
    region: RegionName,
    server_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Get details of a specific server.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}"
    
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

### TODO: Implement update server endpoint with valid fields once available
@router.put("/{server_id}", tags=["Update Server"])
async def update_server(
    region: RegionName,
    server_id: str,
    server_data: Dict[str, Any],
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Update a server's details.
    # TODO: Implement later with valid fields here to update.
    # TODO: Needs to call get server to fetch old data and then update with new data
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.put(url, json={"server": server_data}, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    
    return response.json()

@router.delete("/{server_id}", tags=["Delete Server"])
async def delete_server(
    region: RegionName,
    server_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Delete a server.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}"
    
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
    
    return {"status": "success", "message": "Server deleted successfully"}

@router.post("/{server_id}/rebuild-with-keypair")
async def rebuild_server_with_keypair(
    region: RegionName,
    keypair_name: dict = Body(...),
    server_id: str = Path(...),
    preserve_data: bool = True,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Rebuild server with new key pair (only supported method for existing VMs)
    """
    # 1. Get original server details to obtain imageRef
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    server_url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    try:
        # Get current server details
        server_resp = await client.get(server_url, headers=headers)
        server_data = server_resp.json()["server"]
        
        current_metadata = server_resp.json()["server"]["metadata"]

        # 2. Prepare rebuild payload
        rebuild_url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}/action"
        payload = {
            "rebuild": {
                "imageRef": server_data["image"]["id"],
                "key_name": keypair_name["key_name"],
                "preserve_ephemeral": preserve_data,
                # Optional: Add metadata to track rebuilds
                "metadata": {
                    **current_metadata,
                    "rebuild_reason": "keypair_association",
                    "original_keypair": str(server_data.get("key_name", "none")),
                    "new_keypair": str(keypair_name["key_name"])
                }
            }
        }
        
        # 3. Execute rebuild
        rebuild_resp = await client.post(rebuild_url, json=payload, headers=headers)
        if rebuild_resp.status_code != 202:
            raise HTTPException(
                status_code=rebuild_resp.status_code,
                detail=f"Rebuild failed: {rebuild_resp.text}"
            )
        
        return {
            "status": "success",
            "message": "Server rebuild initiated with new keypair",
            "admin_pass": rebuild_resp.json().get("adminPass", "Not applicable for keypair access")
        }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API error: {e.response.text}"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required data in server response: {str(e)}"
        )
    
@router.post("/{server_id}/os-volume_attachments")
async def attach_volume(
    region: RegionName,
    server_id: str = Path(...),
    attachment_data: VolumeAttachmentCreate = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Attach a volume to a server
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}/os-volume_attachments"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    payload = {
        "volumeAttachment": attachment_data.dict(exclude_none=True)
    }
    
    try:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 202:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to attach volume: {response.text}"
            )
        return response.json()["volumeAttachment"]
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection error while attaching volume: {str(e)}"
        )

@router.delete("/{server_id}/os-volume_attachments/{volume_id}")
async def detach_volume(
    region: RegionName,
    server_id: str = Path(...),
    volume_id: str = Path(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Detach a volume from a server
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}/os-volume_attachments/{volume_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    try:
        response = await client.delete(url, headers=headers)
        if response.status_code != 202:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to detach volume: {response.text}"
            )
        return {"status": "success", "message": "Volume detachment initiated"}
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection error while detaching volume: {str(e)}"
        )

@router.get("/{server_id}/os-volume_attachments")
async def list_volume_attachments(
    region: RegionName,
    server_id: str = Path(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    List all volume attachments for a server
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["servers"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/servers/{server_id}/os-volume_attachments"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["volumeAttachments"]
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to list volume attachments: {e.response.text}"
        )