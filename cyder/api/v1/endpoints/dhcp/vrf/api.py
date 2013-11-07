from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.vrf.models import Vrf, VrfAV


class VrfAVSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    vrf = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vrf-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = VrfAV


class VrfAVViewSet(api.CommonDHCPViewSet):
    model = VrfAV
    serializer_class = VrfAVSerializer


class VrfNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-vrf_attributes-detail')

    class Meta:
        model = VrfAV
        fields = api.NestedAVFields


class VrfSerializer(serializers.HyperlinkedModelSerializer):
    vrfav_set = VrfNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Vrf
        depth = 1


class VrfViewSet(api.CommonDHCPViewSet):
    model = Vrf
    serializer_class = VrfSerializer
    avmodel = VrfAV
