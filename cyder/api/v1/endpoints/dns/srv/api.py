from cyder.api.v1.endpoints.dns import api
from cyder.cydns.srv.models import SRV


class SRVSerializer(api.CommonDNSSerializer, api.LabelDomainMixin):
    class Meta(api.CommonDNSMeta):
        model = SRV


class SRVViewSet(api.CommonDNSViewSet):
    model = SRV
    serializer_class = SRVSerializer
