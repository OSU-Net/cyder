from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import serializers, viewsets

from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
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


standard_fields = ['id', 'domain']


class FQDNMixin(object):
    def restore_object(self, attrs, instance=None):
        if self.fqdn:
            try:
                self.label, self.domain = ensure_label_domain(self.fqdn)
            except ValidationError, e:
                self._errors['fqdn'] = e.messages


class CommonDNSSerializer(serializers.HyperlinkedModelSerializer):
    comment = serializers.CharField()
    domain = serializers.CharField()
    views = serializers.CharField()


class DomainSerializer(CommonDNSSerializer):
    class Meta:
        model = Domain
        fields = ['name', 'master_domain', 'soa', 'is_reverse', 'dirty',
                'purgeable', 'delegated']

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class CNAMESerializer(CommonDNSSerializer, FQDNMixin):
    class Meta:
        model = CNAME
        fields = CNAME.get_api_fields() + standard_fields


class CNAMEViewSet(viewsets.ModelViewSet):
    queryset = CNAME.objects.all()
    serializer_class = CNAMESerializer


class TXTSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = TXT.get_api_fields() + standard_fields


class TXTViewSet(viewsets.ModelViewSet):
    queryset = TXT.objects.all()
    serializer_class = TXTSerializer


class SRVSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = TXT.get_api_fields() + standard_fields


class SRVViewSet(viewsets.ModelViewSet):
    queryset = SRV.objects.all()
    serializer_class = SRVSerializer


class MXSerializer(CommonDNSSerializer):
    class Meta:
        model = MX
        fields = MX.get_api_fields() + standard_fields


class MXViewSet(viewsets.ModelViewSet):
    queryset = MX.objects.all()
    serializer_class = MXSerializer


class SSHFPSerializer(CommonDNSSerializer):
    class Meta:
        model = SSHFP
        fields = SSHFP.get_api_fields() + standard_fields


class SSHFPViewSet(viewsets.ModelViewSet):
    queryset = SSHFP.objects.all()
    serializer_class = SSHFPSerializer


class AddressRecordSerializer(CommonDNSSerializer):
    class Meta:
        model = AddressRecord
        fields = AddressRecord.get_api_fields() + standard_fields


class AddressRecordViewSet(viewsets.ModelViewSet):
    queryset = AddressRecord.objects.all()
    serializer_class = AddressRecordSerializer


class NameserverSerializer(CommonDNSSerializer):
    class Meta:
        models = Nameserver
        fields = Nameserver.get_api_fields() + standard_fields


class NameserverViewSet(viewsets.ModelViewSet):
    queryset = Nameserver.objects.all()
    serializer_class = NameserverSerializer


class PTRSerializer(CommonDNSSerializer):
    class Meta:
        models = PTR
        fields = PTR.get_api_fields() + standard_fields


class PTRViewSet(viewsets.ModelViewSet):
    queryset = PTR.objects.all()
    serializer_class = PTRSerializer


class SystemSerializer(CommonDNSSerializer):
    class Meta:
        models = System
        depth = 1


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer


class StaticIntrKeyValueSerializer(CommonDNSSerializer):
    static_interface = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="staticinterface")

    class Meta:
        model = StaticIntrKeyValue


class StaticInterfaceSerializer(CommonDNSSerializer):
    class Meta:
        model = StaticInterface
        fields = StaticInterface.get_api_fields() + standard_fields + ['system',
            'staticintrkeyvalue_set']
        depth = 1


class StaticInterfaceViewSet(viewsets.ModelViewSet):
    queryset = StaticInterface.objects.all()
    serializer_class = StaticInterfaceSerializer
