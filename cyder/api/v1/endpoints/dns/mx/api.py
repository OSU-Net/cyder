from rest_framework import serializers

from cyder.api.v1.endpoints.dns import api
from cyder.cydns.mx.models import MX


class MXSerializer(serializers.ModelSerializer):
    label = serializers.CharField()
    domain = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='api-dns-domain-detail')
    views = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')

    class Meta(api.CommonDNSMeta):
        model = MX


class MXViewSet(api.CommonDNSViewSet):
    model = MX
    serializer_class = MXSerializer
