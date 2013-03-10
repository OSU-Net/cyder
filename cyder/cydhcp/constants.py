ALLOW_OPTION_VRF = 'vrf'
ALLOW_OPTION_KNOWN = 'known-client'
ALLOW_OPTION_LEGACY = 'legacy'

ALLOW_OPTIONS = {
    ALLOW_OPTION_VRF: 'Allow members of VRF',
    ALLOW_OPTION_KNOWN: 'Allow known-clients',
    ALLOW_OPTION_LEGACY: 'Allow Ctnr: Legacy Option',
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
