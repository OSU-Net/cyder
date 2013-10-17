from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue


class WorkgroupKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    workgroup = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-workgroup-detail')

    class Meta:
        model = WorkgroupKeyValue


class WorkgroupKeyValueViewSet(api.CommonDHCPViewSet):
    model = WorkgroupKeyValue
    serializer_class = WorkgroupKeyValueSerializer


class WorkgroupNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-workgroup_keyvalues-detail')

    class Meta:
        model = WorkgroupKeyValue
        fields = api.NestedKeyValueFields


class WorkgroupSerializer(serializers.HyperlinkedModelSerializer):
    workgroupkeyvalue_set = WorkgroupNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Workgroup
        depth = 1


class WorkgroupViewSet(api.CommonDHCPViewSet):
    model = Workgroup
    serializer_class = WorkgroupSerializer
    keyvaluemodel = WorkgroupKeyValue
