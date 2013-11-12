from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupAV


class WorkgroupAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    workgroup = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-workgroup-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = WorkgroupAV


class WorkgroupAVViewSet(api.CommonDHCPViewSet):
    model = WorkgroupAV
    serializer_class = WorkgroupAVSerializer


class WorkgroupNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-workgroup_attributes-detail')

    class Meta:
        model = WorkgroupAV
        fields = api.NestedAVFields


class WorkgroupSerializer(serializers.HyperlinkedModelSerializer):
    workgroupav_set = WorkgroupNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Workgroup
        depth = 1


class WorkgroupViewSet(api.CommonDHCPViewSet):
    model = Workgroup
    serializer_class = WorkgroupSerializer
    avmodel = WorkgroupAV
