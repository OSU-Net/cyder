from cyder.api.v1.endpoints.dns import api
from cyder.cydns.txt.models import TXT


class TXTSerializer(api.CommonDNSSerializer, api.LabelDomainMixin):
    class Meta(api.CommonDNSMeta):
        model = TXT


class TXTViewSet(api.CommonDNSViewSet):
    model = TXT
    serializer_class = TXTSerializer
