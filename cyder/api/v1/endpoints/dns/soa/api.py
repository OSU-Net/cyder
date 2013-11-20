from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dns import api
from cyder.cydns.soa.models import SOA, SOAAV


class SOAAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    soa = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-soa-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:  # don't import from api.CommonDNSMeta so we get all fields
        model = SOAAV


class SOAAVViewSet(api.CommonDNSViewSet):
    model = SOAAV
    serializer_class = SOAAVSerializer


class SOANestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dns-soa_attributes-detail')

    class Meta:
        model = SOAAV
        fields = api.NestedKeyValueFields


class SOASerializer(serializers.HyperlinkedModelSerializer):
    soaav_set = SOANestedKeyValueSerializer(many=True)

    class Meta(api.CommonDNSMeta):
        model = SOA


class SOAViewSet(api.CommonDNSViewSet):
    model = SOA
    serializer_class = SOASerializer
    avmodel = SOAAV
