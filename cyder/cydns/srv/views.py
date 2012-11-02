from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.views import cydns_list_create_record
from cyder.cydns.srv.models import SRV
from cyder.cydns.srv.forms import SRVForm


class SRVView(object):
    model = SRV
    form_class = SRVForm
    queryset = SRV.objects.all()


class SRVDeleteView(SRVView, CydnsDeleteView):
    """SRV Delete View"""


class SRVDetailView(SRVView, CydnsDetailView):
    """SRV Detail View"""
    template_name = 'srv/srv_detail.html'


class SRVCreateView(SRVView, CydnsCreateView):
    """SRV Create View"""


class SRVUpdateView(SRVView, CydnsUpdateView):
    """SRV Update View"""
