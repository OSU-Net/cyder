from rest_framework import serializers

from cyder.api.v1.endpoints.dns import api
from cyder.cydns.ptr.models import PTR


class PTRSerializer(api.CommonDNSSerializer):
    reverse_domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api-dns-domain-detail")

    class Meta(api.CommonDNSMeta):
        model = PTR


class PTRViewSet(api.CommonDNSViewSet):
    model = PTR
    serializer_class = PTRSerializer
