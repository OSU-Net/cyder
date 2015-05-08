from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface


class DynamicInterfaceSerializer(serializers.ModelSerializer):
    system = serializers.HyperlinkedRelatedField(
        view_name='api-core-system-detail')
    range = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-range-detail')
    workgroup = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-workgroup-detail', required=False)

    class Meta(api.CommonDHCPMeta):
        model = DynamicInterface
        depth = 1


class DynamicInterfaceViewSet(api.CommonDHCPViewSet):
    model = DynamicInterface
    serializer_class = DynamicInterfaceSerializer
