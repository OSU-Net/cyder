# Create your views here.
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.views import CydnsListView
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.sshfp.forms import SSHFPForm


class SSHFPView(object):
    model = SSHFP
    form_class = SSHFPForm
    queryset = SSHFP.objects.all()
    extra_context = {'record_type': 'sshfp'}


class SSHFPDeleteView(SSHFPView, CydnsDeleteView):
    """ """


class SSHFPDetailView(SSHFPView, CydnsDetailView):
    """ """
    template_name = 'sshfp/sshfp_detail.html'


class SSHFPCreateView(SSHFPView, CydnsCreateView):
    """ """


class SSHFPUpdateView(SSHFPView, CydnsUpdateView):
    """ """


class SSHFPListView(SSHFPView, CydnsListView):
    """ """
