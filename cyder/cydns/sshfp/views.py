# Create your views here.
from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsUpdateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.sshfp.forms import SSHFPForm


class SSHFPView(object):
    model = SSHFP
    form_class = SSHFPForm
    queryset = SSHFP.objects.all()


class SSHFPDeleteView(SSHFPView, MozdnsDeleteView):
    """ """


class SSHFPDetailView(SSHFPView, MozdnsDetailView):
    """ """
    template_name = 'sshfp/sshfp_detail.html'


class SSHFPCreateView(SSHFPView, MozdnsCreateView):
    """ """


class SSHFPUpdateView(SSHFPView, MozdnsUpdateView):
    """ """


class SSHFPListView(SSHFPView, MozdnsListView):
    """ """
