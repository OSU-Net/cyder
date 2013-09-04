from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.api.v1.endpoints.dns.api import CommonDNSSerializer
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticIntrKeyValue)


class StaticIntrKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    static_interface = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api-dhcp-staticinterface-detail")

    class Meta:
        model = StaticIntrKeyValue


class StaticIntrKeyValueViewSet(api.CommonDHCPViewSet):
    model = StaticIntrKeyValue
    serializer_class = StaticIntrKeyValueSerializer


class StaticIntrNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-staticinterface_keyvalues-detail')

    class Meta:
        model = StaticIntrKeyValue
        fields = api.NestedKeyValueFields


class StaticInterfaceSerializer(CommonDNSSerializer):
    system = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-system-detail')
    staticintrkeyvalue_set = StaticIntrNestedKeyValueSerializer(many=True)
    ctnr = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-ctnr-detail')
    reverse_domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-domain-detail')
    workgroup = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-workgroup-detail')
    vrf = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vrf-detail')
    domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-domain-detail')

    class Meta(api.CommonDHCPMeta):
        model = StaticInterface
        depth = 1


class StaticInterfaceViewSet(api.CommonDHCPViewSet):
    model = StaticInterface
    serializer_class = StaticInterfaceSerializer
    keyvaluemodel = StaticIntrKeyValue

