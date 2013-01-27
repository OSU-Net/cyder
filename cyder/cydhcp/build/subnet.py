import chili_manage
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
#from cyder.cydhcp.interface.dynamic_intr.models import DynamicIntrfKeyValue
from cyder.cydhcp.network.utils import calc_networks
#from django.core.exceptions import ObjectDoesNotExist, ValidationError
from cyder.core.ctnr.models import Ctnr
#from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue


# This doesn't work for IPv6


def build_subnet(network, raw=False):
    """The cydhcp function of building DHCP files.

    :param network: The network that will be searched for
        :ref:`StaticInterface` instances.
    :type network: :class:`StaticInterface`
    """
    # All interface objects that are within this network and have dhcp_enabled.
    # TODO, make this work with IPv6
    if network.ip_type == '6':
        raise NotImplemented()
    network.update_network()
    network_raw_include = network.dhcpd_raw_include
    network_statements = NetworkKeyValue.objects.filter(
                                network=network, is_statement=True)
    network_options = NetworkKeyValue.objects.filter(
                                network=network, is_option=True)
    network.update_attrs()
    ip_lower_start = int(network.network.network)
    ip_lower_end = int(network.network.broadcast) - 1
    # TODO deal with ipv6 eventaully
    intrs = StaticInterface.objects.filter(ip_upper=0,
            ip_lower__gte=ip_lower_start, ip_lower__lte=ip_lower_end,
            dhcp_enabled=True, ip_type='4')
    ranges = network.range_set.all()
    build_str = "\nsubnet {0} netmask {1} {{\n".format(
            network.network.network, network.network.netmask)
    if not raw:
        build_str += "\t# Network Statements\n"
        for statement in network_statements:
            build_str += "\t{0};\n".format(statement)
        build_str += "\n"
        build_str += "\t# Network Options\n"
        for option in network_options:
            build_str += "\t{0};\n".format(option)
        build_str += "\n"
        # This needs to be documented and may have bugs
        if network_raw_include:
            build_str += "\t# Raw Network Options\n"
            for line in network_raw_include.split('\n'):
                build_str += "\t{0};\n".format(line)
        build_str += "\n"
    for mrange in ranges:
        build_str += build_pool(mrange)
    for intr in intrs:
        build_str += build_host(intr)
    return build_str + "}\n"


def build_pool(mrange):
    mrange_options = RangeKeyValue.objects.filter(
                     range=mrange, is_option=True)
    mrange_statements = RangeKeyValue.objects.filter(
                        range=mrange, is_statement=True)
    mrange_raw_include = mrange.dhcpd_raw_include
    allow = []
    if mrange.allow == 'vrf':
        vrf = Vrf.objects.get(network=mrange.network)
        allow = ["allow members of {0}".format(vrf.name)]
    if mrange.allow == 'known-client':
        allow = ['allow known clients']
    if mrange.allow == 'legacy':
        allow = ["allow members of \"{0}:{1}:{2}\"".format(
            ctnr.name, mrange.start_str, mrange.end_str)
            for ctnr in Ctnr.objects.filter(ranges=mrange)]
    build_str = "\tpool {\n"
    build_str += "\t\t# Pool Statements\n"
    build_str += "\t\tfailover peer \"dhcp\";\n"
    build_str += "\t\tdeny dynamic bootp clients;\n"
    for statement in mrange_statements:
        build_str += "\t\t{0};\n".format(statement)
    build_str += "\n"
    build_str += "\t\t# Pool Options\n"
    for option in mrange_options:
        build_str += "\t\t{0};\n".format(option)
    build_str += "\n"
    if mrange_raw_include:
        build_str += "\t\t# Raw pool includes\n"
        build_str += "\t\t{0};\n".format(mrange_raw_include)
    build_str += "\t\trange {0} {1};\n".format(mrange.start_str,
                                               mrange.end_str)
    for dhcp_class in allow:
        build_str += "\t\t{0};\n".format(dhcp_class)
    build_str += "\t}\n\n"
    return build_str


def build_host(intr):
    build_str = "\thost {0} {{\n".format(intr.fqdn)
    build_str += "\t\thardware ethernet {0};\n".format(intr.mac)
    if hasattr(intr, 'ip_str'):
        build_str += "\t\tfixed-address {0};\n".format(intr.ip_str)
    if hasattr(intr.attrs, 'hostname'):
        build_str += "\t\toption host-name \"{0}\";\n".format(
            intr.attrs.hostname)
    if hasattr(intr.attrs, 'filename'):
        build_str += "\t\tfilename {0};\n".format(intr.attrs.filename)
    if hasattr(intr.attrs, 'domain_name'):
        build_str += "\t\toption domain-name {0};\n".format(
            intr.attrs.domain_name)
    if hasattr(intr.attrs, 'domain_name_servers'):
        build_str += "\t\toption domain-name-servers {0};\n".format(
            intr.attrs.domain_name_servers)
    return build_str + "\t}\n\n"


def build_group(workgroup):
    static_intrs = StaticInterface.objects.filter(workgroup=workgroup)
    workgroup_statements = WorkgroupKeyValue.objects.filter(
                           workgroup=workgroup, is_statement=True)
    workgroup_options = WorkgroupKeyValue.objects.filter(
                        workgroup=workgroup, is_option=True)
    build_str = "group {\n"
    for statement in workgroup_statements:
        build_str += "\t{0};\n".format(statement)
    for option in workgroup_options:
        build_str += "\t{0};\n".format(option)
    build_str += "\t# Hosts in group {0}\n".format(workgroup.name)
    for intr in static_intrs:
        build_str += build_host(intr)
    return build_str + "}\n"


def build_vrf(vrf):
    build_str = ""
    ranges = Range.objects.filter(network=vrf.network)
    for range in ranges:
        build_str += "# {0} for range {1}:{2}\n".format(
                vrf.name, range.start_str, range.end_str)
        build_str += "\nclass \"{0}:{1}:{2}\" {{\n".format(
                vrf.name, range.start_str, range.end_str)
        build_str += "\tmatch hardware;\n"
        build_str += "}\n"
        intrs = DynamicInterface.objects.filter(vrf=vrf)
        build_str += "# Hosts for {0}\n".format(vrf.name)
        for intr in intrs:
            build_str += "subclass \"{0}:{1}:{2}\" 1:{3};\n".format(vrf.name,
                    range.start_str, range.end_str, intr.mac)
    return build_str


def build_legacy_class(ctnr):
    ranges = ctnr.ranges.all()
    build_str = ""
    for range in ranges:
        build_str += "class \"{0}:{1}:{2} {{\n".format(
                ctnr.name, range.start_str, range.end_str)
        build_str += "\tmatch hardware;\n"
        build_str += "}\n"
        intrs = DynamicInterface.objects.filter(ctnr=ctnr, range=range)
        for intr in intrs:
            build_str += "subclass \"{0}:{1}:{2}\" 1:{3};\n".format(
                    ctnr.name, range.start_str, range.end_str, intr.mac)
    return build_str


def main():
    build_str = "# DHCP Generated from cyder."
    networks = Network.objects.all()
    children = []
    for network in networks:
        _, sub = calc_networks(network)
        if not sub:
            children.append(network)
    for network in children:
        build_str += build_subnet(network)
    for workgroup in Workgroup.objects.all():
        build_str += build_group(workgroup)
    for vrf in Vrf.objects.all():
        build_str += build_vrf(vrf)
    for ctnr in Ctnr.objects.all():
        build_str += build_legacy_class(ctnr)

    f = open("test.conf", 'w')
    f.write(build_str)
    f.close()
main()
