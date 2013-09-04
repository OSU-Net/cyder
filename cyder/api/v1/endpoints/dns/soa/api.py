from rest_framework import serializers

from cyder.api.v1.endpoints.dns import api
from cyder.cydns.soa.models import SOA, SOAKeyValue


class SOAKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    soa = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-soa-detail')

    class Meta: # don't import from api.CommonDNSMeta so we get all fields
        model = SOAKeyValue


class SOAKeyValueViewSet(api.CommonDNSViewSet):
    model = SOAKeyValue
    serializer_class = SOAKeyValueSerializer


class SOANestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dns-soa_keyvalues-detail')

    class Meta:
        model = SOAKeyValue
        fields = api.NestedKeyValueFields


class SOASerializer(serializers.HyperlinkedModelSerializer):
    keyvalue_set = SOANestedKeyValueSerializer(many=True)

    class Meta(api.CommonDNSMeta):
        model = SOA


class SOAViewSet(api.CommonDNSViewSet):
    model = SOA
    serializer_class = SOASerializer
    keyvaluemodel = SOAKeyValue
