from rest_framework import serializers

from cyder.api.v1.endpoints.dns import api
from cyder.cydns.nameserver.models import Nameserver


class NameserverSerializer(api.CommonDNSSerializer):
    domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-domain-detail')

    class Meta(api.CommonDNSMeta):
        model = Nameserver


class NameserverViewSet(api.CommonDNSViewSet):
    model = Nameserver
    serializer_class = NameserverSerializer
