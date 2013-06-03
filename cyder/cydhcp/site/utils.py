from cyder.cydhcp.network.models import Network


def get_networks(site):
    return site.network_set.filter(site=site)

def pretty_sites(sites):
    pretty = [site.name for site in sites]
    return pretty

def get_vlans(site):
    """
    v(S^i) = {N^i^v | N^i e n(S^i)}
    returns a set
    """
    vlans = set()
    for network in site.network_set.all():
        if network.vlan:
            vlans.add(network.vlan)
    return vlans
