from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.api.v1.endpoints.dns.api import CommonDNSSerializer
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticInterfaceAV)


class StaticInterfaceAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    staticinterface = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api-dhcp-staticinterface-detail")
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = StaticInterfaceAV


class StaticInterfaceAVViewSet(api.CommonDHCPViewSet):
    model = StaticInterfaceAV
    serializer_class = StaticInterfaceAVSerializer


class StaticIntrNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-staticinterface_attributes-detail')

    class Meta:
        model = StaticInterfaceAV
        fields = api.NestedAVFields


class StaticInterfaceSerializer(CommonDNSSerializer):
    system = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-system-detail')
    staticinterfaceav_set = StaticIntrNestedKeyValueSerializer(many=True)
    ctnr = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-ctnr-detail')
    reverse_domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-domain-detail')
    workgroup = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-workgroup-detail')
    domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dns-domain-detail')

    class Meta(api.CommonDHCPMeta):
        model = StaticInterface
        depth = 1


class StaticInterfaceViewSet(api.CommonDHCPViewSet):
    model = StaticInterface
    serializer_class = StaticInterfaceSerializer
    avmodel = StaticInterfaceAV
