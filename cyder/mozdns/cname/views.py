from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsUpdateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.cname.models import CNAME
from cyder.mozdns.cname.forms import CNAMEForm


class CNAMEView(object):
    model = CNAME
    form_class = CNAMEForm
    queryset = CNAME.objects.all().order_by('fqdn')


class CNAMEDeleteView(CNAMEView, MozdnsDeleteView):
    """ """


class CNAMEDetailView(CNAMEView, MozdnsDetailView):
    """ """
    template_name = "cname/cname_detail.html"


class CNAMECreateView(CNAMEView, MozdnsCreateView):
    """ """


class CNAMEUpdateView(CNAMEView, MozdnsUpdateView):
    """ """


class CNAMEListView(CNAMEView, MozdnsListView):
    """ """
