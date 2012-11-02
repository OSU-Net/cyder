from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.views import cydns_list_create_record
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cname.forms import CNAMEForm


class CNAMEView(object):
    model = CNAME
    form_class = CNAMEForm
    queryset = CNAME.objects.all().order_by('fqdn')


class CNAMEDeleteView(CNAMEView, CydnsDeleteView):
    """ """


class CNAMEDetailView(CNAMEView, CydnsDetailView):
    """ """
    template_name = "cname/cname_detail.html"


class CNAMECreateView(CNAMEView, CydnsCreateView):
    """ """


class CNAMEUpdateView(CNAMEView, CydnsUpdateView):
    """ """


class CNAMEListView(CNAMEView):
    """ """
