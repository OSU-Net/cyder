from rest_framework import routers

from cyder.api.v1.endpoints import core, dhcp, dns

router = routers.DefaultRouter()


router.register(r'core/ctnr',
                core.ctnr.api.CtnrViewSet,
                base_name='api-core-ctnr')
router.register(r'core/system/keyvalues',
                core.system.api.SystemKeyValueViewSet,
                base_name='api-core-system_keyvalues')
router.register(r'core/system', core.system.api.SystemViewSet,
                base_name='api-core-system')
router.register(r'core/user', core.user.api.UserProfileViewSet,
                base_name='api-core-user')


router.register(r'dhcp/dynamic_interface/keyvalues',
                dhcp.dynamic_interface.api.DynamicIntrKeyValueViewSet,
                base_name='api-dhcp-dynamicinterface_keyvalues')
router.register(r'dhcp/dynamic_interface',
                dhcp.dynamic_interface.api.DynamicInterfaceViewSet,
                base_name='api-dhcp-dynamicinterface')
router.register(r'dhcp/network/keyvalues',
                dhcp.network.api.NetworkKeyValueViewSet,
                base_name='api-dhcp-network_keyvalues')
router.register(r'dhcp/network',
                dhcp.network.api.NetworkViewSet,
                base_name='api-dhcp-network')
router.register(r'dhcp/range/keyvalues',
                dhcp.range.api.RangeKeyValueViewSet,
                base_name='api-dhcp-range_keyvalues')
router.register(r'dhcp/range',
                dhcp.range.api.RangeViewSet,
                base_name='api-dhcp-range')
router.register(r'dhcp/site/keyvalues',
                dhcp.site.api.SiteKeyValueViewSet,
                base_name='api-dhcp-site_keyvalues')
router.register(r'dhcp/site',
                dhcp.site.api.SiteViewSet,
                base_name='api-dhcp-site')
router.register(r'dhcp/static_interface/keyvalues',
                dhcp.static_interface.api.StaticIntrKeyValueViewSet,
                base_name='api-dhcp-staticinterface_keyvalues')
router.register(r'dhcp/static_interface',
                dhcp.static_interface.api.StaticInterfaceViewSet,
                base_name='api-dhcp-staticinterface')
router.register(r'dhcp/vlan/keyvalues',
                dhcp.vlan.api.VlanKeyValueViewSet,
                base_name='api-dhcp-vlan_keyvalues')
router.register(r'dhcp/vlan',
                dhcp.vlan.api.VlanViewSet,
                base_name='api-dhcp-vlan')
router.register(r'dhcp/vrf/keyvalues',
                dhcp.vrf.api.VrfKeyValueViewSet,
                base_name='api-dhcp-vrf_keyvalues')
router.register(r'dhcp/vrf',
                dhcp.vrf.api.VrfViewSet,
                base_name='api-dhcp-vrf')
router.register(r'dhcp/workgroup/keyvalues',
                dhcp.workgroup.api.WorkgroupKeyValueViewSet,
                base_name='api-dhcp-workgroup_keyvalues')
router.register(r'dhcp/workgroup',
                dhcp.workgroup.api.WorkgroupViewSet,
                base_name='api-dhcp-workgroup')


router.register(r'dns/address_record',
                dns.address_record.api.AddressRecordViewSet,
                base_name='api-dns-addressrecord')
router.register(r'dns/cname',
                dns.cname.api.CNAMEViewSet,
                base_name='api-dns-cname')
router.register(r'dns/domain',
                dns.domain.api.DomainViewSet,
                base_name='api-dns-domain')
router.register(r'dns/mx',
                dns.mx.api.MXViewSet,
                base_name='api-dns-mx')
router.register(r'dns/nameserver',
                dns.nameserver.api.NameserverViewSet,
                base_name='api-dns-nameserver')
router.register(r'dns/ptr',
                dns.ptr.api.PTRViewSet,
                base_name='api-dns-ptr')
router.register(r'dns/soa/keyvalues',
                dns.soa.api.SOAKeyValueViewSet,
                base_name='api-dns-soa_keyvalues')
router.register(r'dns/soa',
                dns.soa.api.SOAViewSet,
                base_name='api-dns-soa')
router.register(r'dns/srv',
                dns.srv.api.SRVViewSet,
                base_name='api-dns-srv')
router.register(r'dns/sshfp',
                dns.sshfp.api.SSHFPViewSet,
                base_name='api-dns-sshfp')
router.register(r'dns/txt',
                dns.txt.api.TXTViewSet,
                base_name='api-dns-txt')
