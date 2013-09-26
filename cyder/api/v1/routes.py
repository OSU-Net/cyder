from rest_framework import routers

from cyder.api.v1.endpoints.core.ctnr.api import CtnrViewSet
from cyder.api.v1.endpoints.core.system.api import SystemKeyValueViewSet
from cyder.api.v1.endpoints.core.system.api import SystemViewSet
from cyder.api.v1.endpoints.core.user.api import UserProfileViewSet
from cyder.api.v1.endpoints.dhcp.dynamic_interface.api import \
    DynamicIntrKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.dynamic_interface.api import \
    DynamicInterfaceViewSet
from cyder.api.v1.endpoints.dhcp.network.api import NetworkKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.network.api import NetworkViewSet
from cyder.api.v1.endpoints.dhcp.range.api import RangeKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.range.api import RangeViewSet
from cyder.api.v1.endpoints.dhcp.site.api import SiteKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.site.api import SiteViewSet
from cyder.api.v1.endpoints.dhcp.static_interface.api import \
    StaticIntrKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.static_interface.api import \
    StaticInterfaceViewSet
from cyder.api.v1.endpoints.dhcp.vlan.api import VlanKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.vlan.api import VlanViewSet
from cyder.api.v1.endpoints.dhcp.vrf.api import VrfKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.vrf.api import VrfViewSet
from cyder.api.v1.endpoints.dhcp.workgroup.api import WorkgroupKeyValueViewSet
from cyder.api.v1.endpoints.dhcp.workgroup.api import WorkgroupViewSet
from cyder.api.v1.endpoints.dns.address_record.api import AddressRecordViewSet
from cyder.api.v1.endpoints.dns.cname.api import CNAMEViewSet
from cyder.api.v1.endpoints.dns.domain.api import DomainViewSet
from cyder.api.v1.endpoints.dns.mx.api import MXViewSet
from cyder.api.v1.endpoints.dns.nameserver.api import NameserverViewSet
from cyder.api.v1.endpoints.dns.ptr.api import PTRViewSet
from cyder.api.v1.endpoints.dns.soa.api import SOAKeyValueViewSet
from cyder.api.v1.endpoints.dns.soa.api import SOAViewSet
from cyder.api.v1.endpoints.dns.srv.api import SRVViewSet
from cyder.api.v1.endpoints.dns.sshfp.api import SSHFPViewSet
from cyder.api.v1.endpoints.dns.txt.api import TXTViewSet


router = routers.DefaultRouter()


router.register(r'core/ctnr', CtnrViewSet, base_name='api-core-ctnr')
router.register(r'core/system/keyvalues', SystemKeyValueViewSet,
                base_name='api-core-system_keyvalues')
router.register(r'core/system', SystemViewSet, base_name='api-core-system')
router.register(r'core/user', UserProfileViewSet, base_name='api-core-user')


router.register(r'dhcp/dynamic_interface/keyvalues',
                DynamicIntrKeyValueViewSet,
                base_name='api-dhcp-dynamicinterface_keyvalues')
router.register(r'dhcp/dynamic_interface', DynamicInterfaceViewSet,
                base_name='api-dhcp-dynamicinterface')
router.register(r'dhcp/network/keyvalues', NetworkKeyValueViewSet,
                base_name='api-dhcp-network_keyvalues')
router.register(r'dhcp/network', NetworkViewSet, base_name='api-dhcp-network')
router.register(r'dhcp/range/keyvalues', RangeKeyValueViewSet,
                base_name='api-dhcp-range_keyvalues')
router.register(r'dhcp/range', RangeViewSet, base_name='api-dhcp-range')
router.register(r'dhcp/site/keyvalues', SiteKeyValueViewSet,
                base_name='api-dhcp-site_keyvalues')
router.register(r'dhcp/site', SiteViewSet, base_name='api-dhcp-site')
router.register(r'dhcp/static_interface/keyvalues', StaticIntrKeyValueViewSet,
                base_name='api-dhcp-staticinterface_keyvalues')
router.register(r'dhcp/static_interface', StaticInterfaceViewSet,
                base_name='api-dhcp-staticinterface')
router.register(r'dhcp/vlan/keyvalues', VlanKeyValueViewSet,
                base_name='api-dhcp-vlan_keyvalues')
router.register(r'dhcp/vlan', VlanViewSet, base_name='api-dhcp-vlan')
router.register(r'dhcp/vrf/keyvalues', VrfKeyValueViewSet,
                base_name='api-dhcp-vrf_keyvalues')
router.register(r'dhcp/vrf', VrfViewSet, base_name='api-dhcp-vrf')
router.register(r'dhcp/workgroup/keyvalues', WorkgroupKeyValueViewSet,
                base_name='api-dhcp-workgroup_keyvalues')
router.register(r'dhcp/workgroup', WorkgroupViewSet,
                base_name='api-dhcp-workgroup')


router.register(r'dns/address_record', AddressRecordViewSet,
                base_name='api-dns-addressrecord')
router.register(r'dns/cname', CNAMEViewSet, base_name='api-dns-cname')
router.register(r'dns/domain', DomainViewSet, base_name='api-dns-domain')
router.register(r'dns/mx', MXViewSet, base_name='api-dns-mx')
router.register(r'dns/nameserver', NameserverViewSet,
                base_name='api-dns-nameserver')
router.register(r'dns/ptr', PTRViewSet, base_name='api-dns-ptr')
router.register(r'dns/soa/keyvalues', SOAKeyValueViewSet,
                base_name='api-dns-soa_keyvalues')
router.register(r'dns/soa', SOAViewSet, base_name='api-dns-soa')
router.register(r'dns/srv', SRVViewSet, base_name='api-dns-srv')
router.register(r'dns/sshfp', SSHFPViewSet, base_name='api-dns-sshfp')
router.register(r'dns/txt', TXTViewSet, base_name='api-dns-txt')
