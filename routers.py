from auth import auth_router
from networks import networks_router
from networks.security_groups import security_groups_router
from networks.security_group_rules import security_group_rules_router
from networks.ports import ports_router
from networks.subnets import subnets_router
from servers import servers_router
from servers.keypair import keypair_router
from storage import storage_router

all_routers = [auth_router, networks_router, servers_router, storage_router, keypair_router, security_groups_router, security_group_rules_router, ports_router, subnets_router]

