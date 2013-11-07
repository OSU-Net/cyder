from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.vlan.models import Vlan, VlanAV


class VlanAVSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    vlan = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vlan-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = VlanAV


class VlanAVViewSet(api.CommonDHCPViewSet):
    model = VlanAV
    serializer_class = VlanAVSerializer


class VlanNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-vlan_attributes-detail')

    class Meta:
        model = VlanAV
        fields = api.NestedAVFields


class VlanSerializer(serializers.HyperlinkedModelSerializer):
    vlanav_set = VlanNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Vlan
        depth = 1


class VlanViewSet(api.CommonDHCPViewSet):
    model = Vlan
    serializer_class = VlanSerializer
    avmodel = VlanAV
