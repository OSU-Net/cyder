from cyder.api.v1.endpoints.dns import api
from cyder.cydns.address_record.models import AddressRecord


class AddressRecordSerializer(api.CommonDNSSerializer, api.LabelDomainMixin):
    class Meta(api.CommonDNSMeta):
        model = AddressRecord


class AddressRecordViewSet(api.CommonDNSViewSet):
    model = AddressRecord
    serializer_class = AddressRecordSerializer
