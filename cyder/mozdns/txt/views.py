# Create your views here.
from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsUpdateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.txt.models import TXT
from cyder.mozdns.txt.forms import TXTForm


class TXTView(object):
    model = TXT
    form_class = TXTForm
    queryset = TXT.objects.all()


class TXTDeleteView(TXTView, MozdnsDeleteView):
    """ """


class TXTDetailView(TXTView, MozdnsDetailView):
    """ """
    template_name = 'txt/txt_detail.html'


class TXTCreateView(TXTView, MozdnsCreateView):
    """ """


class TXTUpdateView(TXTView, MozdnsUpdateView):
    """ """


class TXTListView(TXTView, MozdnsListView):
    """ """
