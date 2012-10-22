from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsUpdateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cname.forms import CNAMEForm


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
