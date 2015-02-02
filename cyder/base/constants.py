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

STATIC = 'st'
DYNAMIC = 'dy'

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
                "static_interface", "dynamic_interface", "workgroup_av",
                "vrf_av", "vlan_av", "site_av", "range_av", "network_av",
                "static_interface_av", "dynamic_interface_av",)

DNS_OBJECTS = ("address_record", "cname", "domain", "mx", "nameserver", "ptr",
               "soa", "srv", "sshfp", "txt", "view",)

CORE_OBJECTS = ("ctnr_users", "ctnr", "user", "system")


def get_klasses(obj_type):
    from cyder.cydns.address_record.forms import AddressRecordForm
    from cyder.cydns.cname.forms import CNAMEForm
    from cyder.core.ctnr.forms import CtnrForm
    from cyder.cydns.domain.forms import DomainForm
    from cyder.cydhcp.interface.dynamic_intr.forms import (DynamicInterfaceForm,
                                                           DynamicInterfaceAVForm)
    from cyder.cydns.mx.forms import MXForm
    from cyder.cydns.nameserver.forms import NameserverForm
    from cyder.cydhcp.network.forms import NetworkForm, NetworkAVForm
    from cyder.cydns.ptr.forms import PTRForm
    from cyder.cydhcp.range.forms import RangeForm, RangeAVForm
    from cyder.cydhcp.site.forms import SiteForm, SiteAVForm
    from cyder.cydns.soa.forms import SOAForm, SOAAVForm
    from cyder.cydns.srv.forms import SRVForm
    from cyder.cydns.sshfp.forms import SSHFPForm
    from cyder.core.system.forms import SystemForm, SystemAVForm
    from cyder.cydhcp.interface.static_intr.forms import (StaticInterfaceForm,
                                                          StaticInterfaceAVForm)
    from cyder.cydns.txt.forms import TXTForm
    from cyder.cydhcp.vlan.forms import VlanForm, VlanAVForm
    from cyder.cydhcp.vrf.forms import VrfForm, VrfAVForm
    from cyder.cydhcp.workgroup.forms import WorkgroupForm, WorkgroupAVForm

    from cyder.models import (
        AddressRecord, CNAME, Ctnr, Domain, DynamicInterface, DynamicInterfaceAV,
        MX, Nameserver, Network, NetworkAV, PTR, Range, RangeAV, Site, SiteAV, SOA,
        SOAAV, SRV, SSHFP, StaticInterface, StaticInterfaceAV, System, SystemAV,
        TXT, Vlan, VlanAV, Vrf, VrfAV, Workgroup, WorkgroupAV
    )


    klasses = {
        'address_record': (AddressRecord, AddressRecordForm),
        'cname': (CNAME, CNAMEForm),
        'ctnr': (Ctnr, CtnrForm),
        'domain': (Domain, DomainForm),
        'dynamic_interface': (DynamicInterface, DynamicInterfaceForm),
        'dynamic_interface_av': (DynamicInterfaceAV, DynamicInterfaceAVForm),
        'mx': (MX, MXForm),
        'nameserver': (Nameserver, NameserverForm),
        'network': (Network, NetworkForm),
        'network_av': (NetworkAV, NetworkAVForm),
        'ptr': (PTR, PTRForm),
        'range': (Range, RangeForm),
        'range_av': (RangeAV, RangeAVForm),
        'site': (Site, SiteForm),
        'site_av': (SiteAV, SiteAVForm),
        'soa': (SOA, SOAForm),
        'soa_av': (SOAAV, SOAAVForm),
        'srv': (SRV, SRVForm),
        'sshfp': (SSHFP, SSHFPForm),
        'static_interface': (StaticInterface, StaticInterfaceForm),
        'static_interface_av': (StaticInterfaceAV, StaticInterfaceAVForm),
        'system': (System, SystemForm),
        'system_av': (SystemAV, SystemAVForm),
        'txt': (TXT, TXTForm),
        'vlan': (Vlan, VlanForm),
        'vlan_av': (VlanAV, VlanAVForm),
        'vrf': (Vrf, VrfForm),
        'vrf_av': (VrfAV, VrfAVForm),
        'workgroup': (Workgroup, WorkgroupForm),
        'workgroup_av': (WorkgroupAV, WorkgroupAVForm),
    }

    return klasses[obj_type]
