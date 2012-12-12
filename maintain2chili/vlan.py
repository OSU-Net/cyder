
from optparse import optionParser
from ConfigParser improt ConfigParser

import chili_manage
import fix_maintain, maintain_dump

from utilities import get_cursor, long2ip, ip2long, clean_mac, config
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from cyder.cydhcp.network.models import Network

cursor = get_cursor('maintain_sb')

def calculate_prefix(netmask):
    bits = 0
    while netmask > 0:
        if netmask & 1 == 1:
            bits += 1
        netmask >>= 1
    return bits

"""
Maintain tables without foriegn keys

workgroup
zone
vlan
"""







"""
 Subnets have a forign key to vlans.  Vlans have no foriegn keys and need
 to be migrated before we start migrating the subnets table..
"""

def gen_vlans():
    cursor.execute("SELECT * FROM Vlan")
    for id, name, vlan_id in cursur.fetchall():
        kwarg = {'id': id, 'name': name, 'number': vlan_id }
        new_vlan, _  = Vlan.objects.get_or_create(name=name, number=vlan_id)

def gen_vlan(id):
    cursor.execute("SELECT * FROM Vlan WHERE id = '%s';"%id)
    _, name, number = cursor.fetchone()
    new_vlan, _ = Vlan.objects.get_or_create(name=name, number=number)
    return new_vlan

def gen_subnets():
    cursor.execute("SELECT * FROM Subnet")

def gen_subnet(record):
    _, name, subnet, netmask, vlan = record
    prefixlen = calculate_prefix(netmask)        
    network_str = "{0}/{1}".format(ipaddr.IPv4Address(subnet), prefixlen)
    new_subnet, _ = Network.objects.get_or_create(vlan=vlan, ip_type='4',
         ip_lower=0, ip_upper=subnet, network_str=network_str, 
         prefixlen = prefixlen)
    return new_subnet

def gen_ranges(record):
    _. start, end, _, subnet, comment, enabled, parent, allow_hosts = record
    
    
