ALLOW_ANY = 'any'
ALLOW_KNOWN = 'known'
ALLOW_VRF = 'vrf'
ALLOW_LEGACY = 'legacy'
ALLOW_VRF_AND_LEGACY = 'vrf_legacy'

ALLOW_OPTIONS = {
    ALLOW_ANY: 'Allow any client',
    ALLOW_KNOWN: 'Allow known clients',
    ALLOW_VRF: 'Allow members of VRF',
    ALLOW_LEGACY: 'Legacy (allow Ctnrs)',
    ALLOW_VRF_AND_LEGACY: 'Allow members of VRF and Ctnrs',
}

# Some ranges have no allow statements so this option should be able to be
# null. There are a collection of such subnets documented in the migration.
DENY_OPTION_UNKNOWN = 'deny-unknown'
DENY_OPTIONS = {
    DENY_OPTION_UNKNOWN: 'Deny dynamic unknown-clients',
}

STATIC = "st"
DYNAMIC = "dy"
RANGE_TYPE = {
    STATIC: 'Static',
    DYNAMIC: 'Dynamic',
}

DHCP_KEY_VALUES = ("static_interface_kv", "dynamic_interface_kv", "range_kv",
                   "network_kv", "workgroup_kv", "vlan_kv", "vrf_kv",
                   "site_kv")
