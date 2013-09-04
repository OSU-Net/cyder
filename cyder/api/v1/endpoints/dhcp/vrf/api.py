from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue


class VrfKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    vrf = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-vrf-detail')

    class Meta:
        model = VrfKeyValue


class VrfKeyValueViewSet(api.CommonDHCPViewSet):
    model = VrfKeyValue
    serializer_class = VrfKeyValueSerializer


class VrfNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-vrf_keyvalues-detail')

    class Meta:
        model = VrfKeyValue
        fields = api.NestedKeyValueFields


class VrfSerializer(serializers.HyperlinkedModelSerializer):
    vrfkeyvalue_set = VrfNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Vrf
        depth = 1


class VrfViewSet(api.CommonDHCPViewSet):
    model = Vrf
    serializer_class = VrfSerializer
    keyvaluemodel = VrfKeyValue
