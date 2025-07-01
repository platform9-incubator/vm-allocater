import httpx

from fastapi import APIRouter, Depends, HTTPException, Body

from auth import get_auth_token
from config import API_BASE_URLS, get_async_client
from models import RegionName, SecurityGroupRuleCreate, SecurityGroupRuleCreateList, CloudEnvironment

router = APIRouter(prefix="/security_group_rules", tags=["security_group_rules"])

@router.post("/", tags=["Networking - Create Security Group Rule"])
async def create_security_group_rule(
    region: RegionName,
    rule_data_list: SecurityGroupRuleCreateList = Body(...),
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Create a new security group rule.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-group-rules"
    
    headers = {
        "X-Auth-Token": auth["auth_token"],
        "Content-Type": "application/json"
    }
    # print(f"Creating security group rules in {cloud_environment.value} for region {region.value}")
    response_list = []
    for rule_data in rule_data_list.security_group_rules:
        if not isinstance(rule_data, SecurityGroupRuleCreate):
            raise HTTPException(
                status_code=400,
                detail="Invalid security group rules provided"
            )
        rule_dict = rule_data.dict()
        # print(rule_dict)
        request_body = {
            "security_group_rule": {
                "security_group_id": rule_dict["security_group_id"],
                "direction": rule_dict["direction"],
                "protocol": rule_dict["protocol"],
                "ethertype": rule_dict["ethertype"],
                "port_range_min": rule_dict.get("port_range_min", None),
                "port_range_max": rule_dict.get("port_range_max", None),
                "remote_ip_prefix": rule_dict.get("remote_ip_prefix", None)
            }
        }
        # print(f"Creating security group rule: {request_body}")
        try:
            response = await client.post(url, json=request_body, headers=headers)   
        
            if response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            response_list.append(response.json())
        except httpx.HTTPStatusError as e:
            print(e)
            # raise HTTPException(
            #     status_code=e.response.status_code,
            #     detail=f"Failed to create security group rule: {e.response.text}"
            # )
        except Exception as e:
            print(e)
            # raise HTTPException(
            #     status_code=500,
            #     detail=f"An unexpected error occurred: {str(e)}"
            # )
        print("\n", response_list)
    # print(f"Created security group rules: {response_list}")
    return response_list

@router.get("/", tags=["Networking - List Security Group Rules"])
async def list_security_group_rule(
    region: RegionName,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Get details of a specific security group rule.
    # TODO: Give security rule wrt particular user only
    # TODO: Maybe store all security group rules metadata in local database MySQL or MongoDB
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-group-rules"
    
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

@router.get("/{rule_id}", tags=["Networking - Get Security Group Rule"])
async def get_security_group_rule(
    region: RegionName,
    rule_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Get details of a specific security group rule.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-group-rules/{rule_id}"
    
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

@router.delete("/{rule_id}", tags=["Networking - Delete Security Group Rule"])
async def delete_security_group_rule(
    region: RegionName,
    rule_id: str,
    cloud_environment: CloudEnvironment = CloudEnvironment.OSPC,
    client: httpx.AsyncClient = Depends(get_async_client)
):
    """
    Delete a security group rule.
    """
    auth: dict = await get_auth_token(cloud_environment, region, client)

    base_url = API_BASE_URLS[cloud_environment.value]["networking"]
    url = f"{base_url.format(region=region.value)}/security-group-rules/{rule_id}"
    
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
    
    return {"status": "success", "message": "Security group rule deleted successfully"}
