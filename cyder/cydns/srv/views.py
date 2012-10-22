from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsUpdateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.srv.models import SRV
from cyder.cydns.srv.forms import SRVForm


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
