from rest_framework import routers

from cyder.api.v1 import api


"""All base names are prefixed with 'api-' to disambiguate API views from
standard Django/Jinja2 views.
"""
router = routers.DefaultRouter()
router.register(r'cname', api.CNAMEViewSet, base_name='api-cname')
router.register(r'domain', api.DomainViewSet, base_name='api-domain')
router.register(r'txt', api.TXTViewSet, base_name='api-txt')
router.register(r'srv', api.SRVViewSet, base_name='api-srv')
router.register(r'mx', api.MXViewSet, base_name='api-mx')
router.register(r'addressrecord', api.AddressRecordViewSet,
                base_name='api-addressrecord')
router.register(r'nameserver', api.NameserverViewSet,
                base_name='api-nameserver')
router.register(r'ptr', api.PTRViewSet, base_name='api-ptr')
router.register(r'sshfp', api.SSHFPViewSet, base_name='api-sshfp')
router.register(r'srv', api.SRVViewSet, base_name='api-srv')
router.register(r'system', api.SystemViewSet, base_name='api-system')
router.register(r'system-keyvalues', api.SystemKeyValueViewSet,
                base_name='api-system-keyvalues')
router.register(r'staticinterface', api.StaticInterfaceViewSet,
                base_name='api-staticinterface')
router.register(r'staticinterface-keyvalues', api.StaticIntrKeyValueViewSet,
                base_name='api-staticinterface-keyvalues')
router.register(r'dynamicinterface', api.DynamicInterfaceViewSet,
                base_name='api-dynamicinterface')
router.register(r'dynamicinterface-keyvalues', api.DynamicIntrKeyValueViewSet,
                base_name='api-dynamicinterface-keyvalues')
urlpatterns = router.urls
