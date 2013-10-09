from cyder.api.v1.endpoints.dns import api
from cyder.cydns.sshfp.models import SSHFP


class SSHFPSerializer(api.CommonDNSSerializer, api.LabelDomainMixin):
    class Meta (api.CommonDNSMeta):
        model = SSHFP


class SSHFPViewSet(api.CommonDNSViewSet):
    model = SSHFP
    serializer_class = SSHFPSerializer
