
import chili_manage
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.utils import calc_networks
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.range.models import Range
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
    network_statements = NetworkKeyValue.objects.filter(network=network,
                                                        is_statement=True)
    network_options = NetworkKeyValue.objects.filter(network=network,
                                                        is_option=True)
    network.update_attrs()
    ip_lower_start = int(network.network.network)
    ip_lower_end = int(network.network.broadcast) - 1
    intrs = StaticInterface.objects.filter(ip_upper=0,
            ip_lower__gte=ip_lower_start, ip_lower__lte=ip_lower_end,
            dhcp_enabled=True, ip_type='4')
    ranges = network.range_set.all()

    # Let's assume all options need a ';' appended.
    build_str = "\nsubnet {0} netmask {1} {{\n".format(network.network.network,
                 network.network.netmask)
    build_str += "\n"
    if not raw:
        build_str += "\t# Network Statements\n"
        for statement in network_statements:
            build_str += "\t{0:20} {1};\n".format(statement.key, statement.value)
        build_str += "\n"
        build_str += "\t# Network Options\n"
        for option in network_options:
            build_str += "\toption {0:20} {1};\n".format(option.key, option.value)
        build_str += "\n"

        if network_raw_include:
            for line in network_raw_include.split('\n'):
                build_str += "\t{0}\n".format(line)
        build_str += "\n"

    for mrange in ranges:
        build_str += build_pool(mrange)


    for intr in intrs:
        build_str += build_host(intr)
    return build_str + "}\n"


def build_pool(mrange):
    mrange_options = mrange.rangekeyvalue_set.filter(is_option=True)
    mrange_statements = mrange.rangekeyvalue_set.filter(is_statement=True)
    mrange_raw_include = mrange.dhcpd_raw_include
    build_str = "\tpool {\n"
    build_str += "\t\t# Pool Statements\n"
    for statement in mrange_statements:
        build_str += "\t\t{0:20} {1};\n".format(statement.key,
                                                statement.value)
    build_str += "\n"
    build_str += "\t\t# Pool Options\n"
    for option in mrange_options:
        build_str += "\t\toption {0:20} {1};\n".format(option.key,
                                                       option.value)
    build_str += "\n"

    if mrange_raw_include:
        build_str += "\n\t\t{0}\n".format(mrange_raw_include)
    build_str += "\t\trange {0} {1};\n".format(mrange.start_str,
                                               mrange.end_str)
    build_str += "\t}\n\n"
    return build_str


def build_host(intr):
    build_str = "\thost {0} {{\n".format(intr.fqdn)
    build_str += "\t\thardware ethernet {0};\n".format(intr.mac)
    if hasattr(intr,'ip_str'):
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
    workgroup_statements = WorkgroupKeyValue.objects.filter(workgroup=workgroup, is_statement=True)
    workgroup_options = WorkgroupKeyValue.objects.filter(workgroup=workgroup, is_option=True)
    build_str = "group {\n"
    for statement in workgroup_statements:
        build_str += "\t{0};\n".format(statement)
    for option in workgroup_options:
        build_str += "\toption {0};\n".format(statement)
    build_str += "\t# Hosts in group {0}\n".format(workgroup.name)
    for intr in static_intrs:
        build_str += build_host(intr)
    return build_str + "}\n"


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

    f = open("test.conf", 'w')
    f.write(build_str)
    f.close()
main()
