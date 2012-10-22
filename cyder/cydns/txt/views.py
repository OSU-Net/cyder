# Create your views here.
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.views import CydnsListView
from cyder.cydns.txt.models import TXT
from cyder.cydns.txt.forms import TXTForm


class TXTView(object):
    model = TXT
    form_class = TXTForm
    queryset = TXT.objects.all()


class TXTDeleteView(TXTView, CydnsDeleteView):
    """ """


class TXTDetailView(TXTView, CydnsDetailView):
    """ """
    template_name = 'txt/txt_detail.html'


class TXTCreateView(TXTView, CydnsCreateView):
    """ """


class TXTUpdateView(TXTView, CydnsUpdateView):
    """ """


class TXTListView(TXTView, CydnsListView):
    """ """
