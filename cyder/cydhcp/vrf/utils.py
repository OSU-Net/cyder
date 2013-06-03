from cyder.cydhcp.vrf.models import Vrf

def pretty_vrfs(vrfs):
    pretty = [vrf.name for vrf in vrfs]
    return pretty
