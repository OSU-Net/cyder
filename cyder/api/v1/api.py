from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import decorators, response, serializers, viewsets

from cyder.core.system.models import System, SystemKeyValue
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.models import DynamicIntrKeyValue
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.txt.models import TXT
from cyder.cydns.utils import ensure_label_domain, prune_tree
from cyder.cydns.view.models import View


standard_fields = ['id']


class FQDNMixin(object):
    def restore_object(self, attrs, instance=None):
        if self.fqdn:
            try:
                self.label, self.domain = ensure_label_domain(self.fqdn)
            except ValidationError, e:
                self._errors['fqdn'] = e.messages


class CommonDNSSerializer(serializers.HyperlinkedModelSerializer):
    comment = serializers.CharField()
    views = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')


class CommonDNSViewSet(viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        self.queryset = self.model.objects.all()
        super(CommonDNSViewSet,self).__init__(*args, **kwargs)


class DomainSerializer(serializers.HyperlinkedModelSerializer):
    master_domain = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='api-domain-detail')

    class Meta:
        model = Domain
        fields = ['id', 'name', 'master_domain', 'soa', 'is_reverse', 'dirty',
                'purgeable', 'delegated']


class DomainViewSet(CommonDNSViewSet):
    model = Domain
    serializer_class = DomainSerializer


class CNAMESerializer(CommonDNSSerializer, FQDNMixin):
    class Meta:
        model = CNAME
        fields = standard_fields + CNAME.get_api_fields()


class CNAMEViewSet(CommonDNSViewSet):
    model = CNAME
    serializer_class = CNAMESerializer


class TXTSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = standard_fields + TXT.get_api_fields()


class TXTViewSet(CommonDNSViewSet):
    model = TXT
    serializer_class = TXTSerializer


class SRVSerializer(CommonDNSSerializer):
    class Meta:
        model = SRV
        fields = standard_fields + SRV.get_api_fields()


class SRVViewSet(CommonDNSViewSet):
    model = SRV
    serializer_class = SRVSerializer


class MXSerializer(CommonDNSSerializer):
    class Meta:
        model = MX
        fields = standard_fields + MX.get_api_fields()


class MXViewSet(CommonDNSViewSet):
    model = MX
    serializer_class = MXSerializer


class SSHFPSerializer(CommonDNSSerializer):
    class Meta:
        model = SSHFP
        fields = standard_fields + SSHFP.get_api_fields()


class SSHFPViewSet(viewsets.ModelViewSet):
    model = SSHFP
    serializer_class = SSHFPSerializer


class AddressRecordSerializer(CommonDNSSerializer):
    class Meta:
        model = AddressRecord
        fields = standard_fields + AddressRecord.get_api_fields()


class AddressRecordViewSet(viewsets.ModelViewSet):
    model = AddressRecord
    serializer_class = AddressRecordSerializer


class NameserverSerializer(CommonDNSSerializer):
    domain = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api-domain-detail")

    class Meta:
        model = Nameserver
        fields = standard_fields + Nameserver.get_api_fields()


class NameserverViewSet(viewsets.ModelViewSet):
    model = Nameserver
    serializer_class = NameserverSerializer


class PTRSerializer(CommonDNSSerializer):
    class Meta:
        model = PTR
        fields = standard_fields + PTR.get_api_fields()


class PTRViewSet(viewsets.ModelViewSet):
    model = PTR
    serializer_class = PTRSerializer


class SystemKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    system = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-system-detail')

    class Meta:
        model = SystemKeyValue


class SystemKeyValueViewSet(viewsets.ModelViewSet):
    model = SystemKeyValue
    queryset = SystemKeyValue.objects.all()
    serializer_class = SystemKeyValueSerializer


class SystemNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-system_keyvalues-detail')

    class Meta:
        model = SystemKeyValue
        fields = ['id', 'key', 'value', 'is_quoted']


class SystemSerializer(serializers.ModelSerializer):
    systemkeyvalue_set = SystemNestedKeyValueSerializer(many=True)

    class Meta:
        model = System
        fields = ['id', 'name', 'systemkeyvalue_set']


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    search_fields = ['name']


class StaticIntrKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    static_interface = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api-staticinterface-detail")

    class Meta:
        model = StaticIntrKeyValue


class StaticIntrKeyValueViewSet(viewsets.ModelViewSet):
    model = StaticIntrKeyValue
    queryset = StaticIntrKeyValue.objects.all()
    serializer_class = StaticIntrKeyValueSerializer


class StaticIntrNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
            view_name='api-staticinterface_keyvalues-detail')

    class Meta:
        model = StaticIntrKeyValue
        fields = ['id', 'key', 'value', 'is_quoted']


class StaticInterfaceSerializer(CommonDNSSerializer):
    staticintrkeyvalue_set = StaticIntrNestedKeyValueSerializer(many=True)

    class Meta:
        model = StaticInterface
        fields = (standard_fields + StaticInterface.get_api_fields() +
            ['system', 'staticintrkeyvalue_set'])


class StaticInterfaceViewSet(viewsets.ModelViewSet):
    queryset = StaticInterface.objects.all()
    serializer_class = StaticInterfaceSerializer


class DynamicIntrKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    dynamic_interface = serializers.HyperlinkedRelatedField(
            read_only=True, view_name="api-dynamicinterface-detail")

    class Meta:
        model = DynamicIntrKeyValue


class DynamicIntrKeyValueViewSet(viewsets.ModelViewSet):
    model = DynamicIntrKeyValue
    queryset = DynamicIntrKeyValue.objects.all()
    serializer_class = DynamicIntrKeyValueSerializer


class DynamicIntrNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
            view_name='api-dynamicinterface_keyvalues-detail')

    class Meta:
        model = DynamicIntrKeyValue
        fields = ['id', 'key', 'value', 'is_quoted']


class DynamicInterfaceSerializer(serializers.HyperlinkedModelSerializer):
    dynamicintrkeyvalue_set = DynamicIntrNestedKeyValueSerializer(many=True)

    class Meta:
        model = DynamicInterface
        fields = ['id', 'ctnr', 'workgroup', 'system', 'mac', 'vrf',
            'domain', 'range', 'dhcp_enabled', 'dns_enabled', 'last_seen',
            'dynamicintrkeyvalue_set']
        depth = 1


class DynamicInterfaceViewSet(viewsets.ModelViewSet):
    queryset = DynamicInterface.objects.all()
    serializer_class= DynamicInterfaceSerializer
