ALLOW_ANY = 'a'
ALLOW_KNOWN = 'k'
ALLOW_LEGACY = 'l'
ALLOW_VRF = 'v'

ALLOW_OPTIONS = [
    (ALLOW_ANY, 'ANY: Allow any client'),
    (ALLOW_KNOWN, 'KNOWN: Allow known clients'),
    (ALLOW_LEGACY, "LEGACY: Allow any client that shares at least one of this "
                   "range's containers"),
    (ALLOW_VRF, "VRF: Allow any client that shares this range's VRF"),
]

STATIC = "st"
DYNAMIC = "dy"
RANGE_TYPE = (
    (STATIC, 'Static'),
    (DYNAMIC, 'Dynamic'),
)

DHCP_EAV_MODELS = ("range_av", "network_av", "workgroup_av", "vlan_av",
                   "vrf_av", "site_av")

SYSTEM_INTERFACE_CTNR_ERROR = (
    "Cannot change container; interface's container and system's container "
    "must be the same. Please change the system's container instead.")
DEFAULT_WORKGROUP = 1
