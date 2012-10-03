# Create your views here.
from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsUpdateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.sshfp.models import SSHFP
from cyder.mozdns.sshfp.forms import SSHFPForm


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
