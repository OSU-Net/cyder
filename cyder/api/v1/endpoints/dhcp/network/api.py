from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.network.models import Network, NetworkKeyValue


class NetworkKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    network = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-network-detail')

    class Meta:
        model = NetworkKeyValue


class NetworkKeyValueViewSet(api.CommonDHCPViewSet):
    model = NetworkKeyValue
    serializer_class = NetworkKeyValueSerializer


class NetworkNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-network_keyvalues-detail')

    class Meta:
        model = NetworkKeyValue
        fields = api.NestedKeyValueFields


class NetworkSerializer(api.CommonDHCPSerializer):
    vlan = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vlan-detail')
    site = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')
    vrf = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vrf-detail')
    networkkeyvalue_set = NetworkNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Network
        depth = 1


class NetworkViewSet(api.CommonDHCPViewSet):
    model = Network
    serializer_class = NetworkSerializer
    keyvaluemodel = NetworkKeyValue
