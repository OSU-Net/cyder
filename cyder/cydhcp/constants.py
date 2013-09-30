ALLOW_ANY = 'a'
ALLOW_KNOWN = 'k'
ALLOW_LEGACY = 'l'
ALLOW_VRF = 'v'
ALLOW_LEGACY_AND_VRF = 'b'

ALLOW_OPTIONS = [
    (ALLOW_ANY, 'ANY: Allow any client'),
    (ALLOW_KNOWN, 'KNOWN: Allow known clients'),
    (ALLOW_LEGACY, "LEGACY: Allow any client that shares at least one of this range's containers"),
    (ALLOW_VRF, "VRF: Allow any client that shares this range's VRF"),
    (ALLOW_LEGACY_AND_VRF, 'LEGACY+VRF: Allow any client that shares either a VRF or a container'),
]

STATIC = "st"
DYNAMIC = "dy"
RANGE_TYPE = (
    (STATIC, 'Static'),
    (DYNAMIC, 'Dynamic'),
)

DHCP_KEY_VALUES = ("static_interface_kv", "dynamic_interface_kv", "range_kv",
                   "network_kv", "workgroup_kv", "vlan_kv", "vrf_kv",
                   "site_kv")
