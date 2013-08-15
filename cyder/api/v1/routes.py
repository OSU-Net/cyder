from rest_framework import routers

from cyder.api.v1 import api

router = routers.DefaultRouter()
router.register(r'cname', api.CNAMEViewSet, base_name='cname')
router.register(r'domain', api.DomainViewSet, base_name='domain')
router.register(r'txt', api.TXTViewSet, base_name='txt')
router.register(r'srv', api.SRVViewSet, base_name='srv')
router.register(r'mx', api.MXViewSet, base_name='mx')
router.register(r'addressrecord', api.AddressRecordViewSet,
                base_name='addressrecord')
router.register(r'nameserver', api.NameserverViewSet, base_name='nameserver')
router.register(r'ptr', api.PTRViewSet, base_name='ptr')
router.register(r'system', api.SystemViewSet, base_name='system')
router.register(r'staticinterface', api.StaticInterfaceViewSet,
                base_name='staticinterface')
urlpatterns = router.urls
