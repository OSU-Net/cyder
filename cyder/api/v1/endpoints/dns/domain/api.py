from rest_framework import serializers

from cyder.api.v1.endpoints.dns import api
from cyder.cydns.domain.models import Domain


class DomainSerializer(serializers.HyperlinkedModelSerializer):
    master_domain = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='api-dns-domain-detail')

    class Meta(api.CommonDNSMeta):
        model = Domain


class DomainViewSet(api.CommonDNSViewSet):
    model = Domain
    serializer_class = DomainSerializer
