from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsUpdateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.srv.models import SRV
from cyder.mozdns.srv.forms import SRVForm


class SRVView(object):
    model = SRV
    form_class = SRVForm
    queryset = SRV.objects.all()


class SRVDeleteView(SRVView, MozdnsDeleteView):
    """SRV Delete View"""


class SRVDetailView(SRVView, MozdnsDetailView):
    """SRV Detail View"""
    template_name = 'srv/srv_detail.html'


class SRVCreateView(SRVView, MozdnsCreateView):
    """SRV Create View"""


class SRVUpdateView(SRVView, MozdnsUpdateView):
    """SRV Update View"""


class SRVListView(SRVView, MozdnsListView):
    """SRV List View"""
