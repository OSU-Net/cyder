ACTION_CREATE = 0
ACTION_VIEW = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3
ACTIONS = {
    ACTION_CREATE: 'Create',
    ACTION_VIEW:   'View',
    ACTION_UPDATE: 'Update',
    ACTION_DELETE: 'Delete',
}

LEVEL_GUEST = 0
LEVEL_USER = 1
LEVEL_ADMIN = 2
LEVELS = {
    LEVEL_GUEST: 'Guest',
    LEVEL_USER:  'User',
    LEVEL_ADMIN: 'Admin',
}

IP_TYPE_4 = '4'
IP_TYPE_6 = '6'
IP_TYPES = {
    IP_TYPE_4: 'IPv4',
    IP_TYPE_6: 'IPv6'
}

DHCP_OBJECTS = ("workgroup", "vrf", "vlan", "site", "range", "network",
                "static_interface", "dynamic_interface", "workgroup_kv",
                "vrf_kv", "vlan_kv", "site_kv", "range_kv", "network_kv",
                "static_interface_kv", "dynamic_interface_kv",)

DNS_OBJECTS = ("address_record", "cname", "domain", "mx", "nameserver", "ptr",
               "soa", "srv", "sshfp", "txt", "view",)

CORE_OBJECTS = ("ctnr_users", "ctnr", "user", "system")
