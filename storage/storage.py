import httpx

from fastapi import APIRouter, Depends, HTTPException, Body

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, VolumeCreate, VolumeCreateList, VolumeUpdate, VolumeUpdateList, CloudEnvironment


router = APIRouter(prefix="/volumes", tags=["volumes"])


@router.get("/", tags=["Block Storage - List Volumes"])
async def list_volumes(
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """List all volumes"""
    # TODO: Show only user related volumes, not all volumes in the region
    # TODO: Store volumes metadata in local database MySQL or MongoDB
    try:
        auth: dict = await get_auth_token(cloud_environment, region, client)

        base_url = API_BASE_URLS[cloud_environment.value]["volumes"]
        url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/volumes"
        
        headers = {
            "X-Auth-Token": auth["auth_token"],
            "Content-Type": "application/json"
        }
        
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to list volumes: {e.response.text}"
        )

@router.post("/", tags=["Block Storage - Create Volumes"])
async def create_volume(
    region: RegionName,
    volume_data_list: VolumeCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Create a new volumes"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["volumes"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/volumes"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response_list = []
    for volume_data in volume_data_list.volumes:
        if not isinstance(volume_data, VolumeCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid volume data provided"
            )
        payload = {
            "volume": volume_data.dict(exclude_none=True)
        }
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code not in [200, 201, 202]:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        response_list.append(response.json())
    return response_list

@router.get("")
@router.get("/{volume_id}", tags=["Block Storage - Get Volume"])
async def get_volume(
    region: RegionName,
    volume_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Get volume details"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["volumes"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/volumes/{volume_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }

    response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# TODO: Handle for List of volumes updates together
@router.put("/{volume_id}", tags=["Block Storage - Update Volumes"])
async def update_volume(
    region: RegionName,
    volume_id: str,
    volume_data: VolumeUpdate,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Update volume metadata"""
    # TODO: Handle for List of volumes updates together

    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["volumes"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/volumes/{volume_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.put(url, json={"volume": volume_data.dict(exclude_none=True)}, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.delete("/{volume_id}", tags=["Block Storage - Delete Volume"])
async def delete_volume(
    region: RegionName,
    volume_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """Delete a volume"""
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["volumes"]
    url = f"{base_url.format(region=region.value, tenant_id=auth["tenant_id"])}/volumes/{volume_id}"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    
    response = await client.delete(url, headers=headers)
    if response.status_code not in [202, 204]:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"status": "success", "message": "Volume deletion initiated"}
