from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.network.models import Network, NetworkAV


class NetworkAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    network = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-network-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = NetworkAV


class NetworkAVViewSet(api.CommonDHCPViewSet):
    model = NetworkAV
    serializer_class = NetworkAVSerializer


class NetworkNestedAVSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-network_keyvalues-detail')

    class Meta:
        model = NetworkAV
        fields = api.NestedAVFields


class NetworkSerializer(api.CommonDHCPSerializer):
    vlan = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vlan-detail')
    site = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')
    vrf = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vrf-detail')
    networkav_set = NetworkNestedAVSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Network
        depth = 1


class NetworkViewSet(api.CommonDHCPViewSet):
    model = Network
    serializer_class = NetworkSerializer
    avmodel = NetworkAV
