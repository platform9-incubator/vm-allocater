from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Enums and Models
class CloudEnvironment(str, Enum):
    OSPC = "ospc"
    FLEX = "flex"

class RegionName(str, Enum):
    DFW = "dfw"
    ORD = "ord"
    IAD = "iad"
    LON = "lon"
    SYD = "syd"
    HKG = "hkg"

class AuthRequest(BaseModel):
    username: str
    api_key: str
    environment: CloudEnvironment = Field(..., description="Either 'ospc' or 'flex'")

class TokenResponse(BaseModel):
    token: str
    expires: str
    tenant_id: str

class ServerCreate(BaseModel):
    name: str
    imageRef: str
    flavorRef: str
    metadata: Optional[Dict[str, Any]] = None
    networks: Optional[List[Dict[str, Any]]] = None
    key_name: Optional[str] = None

class ServerCreateList(BaseModel):
    servers: List[ServerCreate] 

class SecurityGroupCreate(BaseModel):
    name: str
    description: str

class SecurityGroupCreateList(BaseModel):
    security_groups: List[SecurityGroupCreate]

class SecurityGroupRuleCreate(BaseModel):
    security_group_id: str
    direction: str
    protocol: str
    port_range_min: Optional[int] = None
    port_range_max: Optional[int] = None
    remote_group_id: Optional[str] = None
    ethertype: str = Field("IPv4", description="Either 'IPv4' or 'IPv6'")

class SecurityGroupRuleCreateList(BaseModel):
    security_group_rules: List[SecurityGroupRuleCreate]
   
class PortCreate(BaseModel):
    network_id: str
    name: Optional[str] = None
    fixed_ips: Optional[List[Dict[str, str]]] = None
    security_groups: Optional[List[str]] = None

class PortCreateList(BaseModel):
    ports: List[PortCreate]
    
# class VolumeCreate(BaseModel):
#     size: int  # in GB
#     volume_type: Optional[str] = None
#     name: Optional[str] = None
#     description: Optional[str] = None
#     availability_zone: Optional[str] = None

# class VolumeCreateList(BaseModel):
#     volumes: List[VolumeCreate]

class VolumeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class VolumeUpdateList(BaseModel):
    volumes: List[VolumeUpdate]

class NetworkCreate(BaseModel):
    name: str
    admin_state_up: bool = True
    shared: bool = False
    tenant_id: Optional[str] = None

class NetworkCreateList(BaseModel):
    networks: List[NetworkCreate]

class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    admin_state_up: Optional[bool] = None
    shared: Optional[bool] = None

class NetworkUpdateList(BaseModel):
    networks: List[NetworkUpdate]

class SubnetCreate(BaseModel):
    network_id: str
    cidr: str
    ip_version: int = Field(4, ge=4, le=6)
    name: Optional[str] = None
    enable_dhcp: bool = True
    gateway_ip: Optional[str] = None
    allocation_pools: Optional[List[Dict[str, str]]] = None
    dns_nameservers: Optional[List[str]] = None

class SubnetCreateList(BaseModel):
    subnets: List[SubnetCreate]

class SubnetUpdate(BaseModel):
    name: Optional[str] = None
    enable_dhcp: Optional[bool] = None
    gateway_ip: Optional[str] = None
    dns_nameservers: Optional[List[str]] = None

class SubnetUpdateList(BaseModel):
    subnets: List[SubnetUpdate]

class VolumeCreate(BaseModel):
    size: int  # in GiB
    display_name: Optional[str] = None
    display_description: Optional[str] = None
    volume_type: Optional[str] = "SATA"  # SATA or SSD
    snapshot_id: Optional[str] = None
    source_volid: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    imageRef: Optional[str] = None  # For bootable volumes

class VolumeCreateList(BaseModel):
    volumes: List[VolumeCreate]

class VolumeResponse(BaseModel):
    id: str
    status: str
    size: int
    display_name: Optional[str]
    display_description: Optional[str]
    volume_type: str
    created_at: datetime
    availability_zone: str
    metadata: Dict[str, str]
    attachments: List[Dict]

class VolumeAttachmentCreate(BaseModel):
    volumeId: str
    device: Optional[str] = None  # None for auto-assignment

class VolumeAttachmentResponse(BaseModel):
    id: str
    device: str
    serverId: str
    volumeId: str

class KeyPairCreate(BaseModel):
    name: str  # Key pair name (must be unique)

class KeyPairImport(BaseModel):
    name: str  # Key pair name (must be unique)
    public_key: str  # SSH public key content

class KeyPairResponse(BaseModel):
    fingerprint: str
    name: str
    private_key: Optional[str] = None  # Only present for newly created keys
    public_key: str
    user_id: str

