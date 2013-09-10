from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.vlan.models import Vlan, VlanKeyValue


class VlanKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    vlan = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vlan-detail')

    class Meta:
        model = VlanKeyValue


class VlanKeyValueViewSet(api.CommonDHCPViewSet):
    model = VlanKeyValue
    serializer_class = VlanKeyValueSerializer


class VlanNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-vlan_keyvalues-detail')

    class Meta:
        model = VlanKeyValue
        fields = api.NestedKeyValueFields


class VlanSerializer(serializers.HyperlinkedModelSerializer):
    vlankeyvalue_set = VlanNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Vlan
        depth = 1


class VlanViewSet(api.CommonDHCPViewSet):
    model = Vlan
    serializer_class = VlanSerializer
    keyvaluemodel = VlanKeyValue
