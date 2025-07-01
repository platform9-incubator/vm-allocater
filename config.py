import httpx
import asyncio

from collections import defaultdict

from models import CloudEnvironment, RegionName

origins = [
    # "http://localhost:5173/",
    "http://localhost:5173"
    # "*",
    # "http://localhost:3000",
]

API_BASE_URLS = {
    CloudEnvironment.OSPC: {
        "identity": "https://identity.api.rackspacecloud.com/v2.0",
        "servers": "https://{region}.servers.api.rackspacecloud.com/v2/{tenant_id}",
        "volumes": "https://{region}.blockstorage.api.rackspacecloud.com/v1/{tenant_id}",
        "networking": "https://{region}.networks.api.rackspacecloud.com/v2.0"
    },
    CloudEnvironment.FLEX: {
        "identity": "https://identity.api.rackspacecloud.com/v2.0",
        "servers": "https://{region}.servers.api.rackspacecloud.com/v2/{tenant_id}",
        "volumes": "https://{region}.blockstorage.api.rackspacecloud.com/v1/{tenant_id}",
        "networking": "https://{region}.networks.api.rackspacecloud.com/v2.0"
    }
}

async def get_async_client():
    async with httpx.AsyncClient() as client:
        yield client

#######################  Temporary in-memory storage for Redis-like functionality ##################
# TODO: Replace with Redis or another persistent storage solution once ready
### Won't work for multi-process applications, but suitable for single-process FastAPI apps ###
### Move to Redis later

temporary_redis = {
    env.value: {
        region.value: {
            "auth_token": None,
            "expires": None,
            "tenant_id": None,
        } for region in RegionName
    } for env in CloudEnvironment
}

# Lock map 
lock_map = defaultdict(asyncio.Lock)

# Read (no lock needed)
def get_token(env, region):
    return temporary_redis[env][region]

# Write (with lock)
async def update_token(env, region, token_data):
    key = f"{env}:{region}"
    async with lock_map[key]:
        temporary_redis[env][region] = token_data

#################################################################################################