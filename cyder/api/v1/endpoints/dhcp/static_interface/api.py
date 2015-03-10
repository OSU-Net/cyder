from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.api.v1.endpoints.dns.api import CommonDNSSerializer
from cyder.cydhcp.interface.static_intr.models import StaticInterface


class StaticInterfaceSerializer(CommonDNSSerializer):
    system = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-system-detail')
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
