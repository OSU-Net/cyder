from rest_framework import routers

from cyder.api.v1 import api


"""All base names are prefixed with 'api-' to disambiguate API views from
standard Django/Jinja2 views.
"""
router = routers.DefaultRouter()
router.register(r'dns/cname', api.CNAMEViewSet, base_name='api-cname')
router.register(r'dns/domain', api.DomainViewSet, base_name='api-domain')
router.register(r'dns/txt', api.TXTViewSet, base_name='api-txt')
router.register(r'dns/srv', api.SRVViewSet, base_name='api-srv')
router.register(r'dns/mx', api.MXViewSet, base_name='api-mx')
router.register(r'dns/address_record', api.AddressRecordViewSet,
                base_name='api-addressrecord')
router.register(r'dns/nameserver', api.NameserverViewSet,
                base_name='api-nameserver')
router.register(r'dns/ptr', api.PTRViewSet, base_name='api-ptr')
router.register(r'dns/sshfp', api.SSHFPViewSet, base_name='api-sshfp')
router.register(r'dns/srv', api.SRVViewSet, base_name='api-srv')
router.register(r'core/system', api.SystemViewSet, base_name='api-system')
router.register(r'dhcp/static_interface', api.StaticInterfaceViewSet,
                base_name='api-staticinterface')
router.register(r'dhcp/dynamic_interface', api.DynamicInterfaceViewSet,
                base_name='api-dynamicinterface')
urlpatterns = router.urls
