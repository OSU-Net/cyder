# Create your views here.
from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsUpdateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.txt.models import TXT
from cyder.cydns.txt.forms import TXTForm


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
