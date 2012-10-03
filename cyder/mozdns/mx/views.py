from cyder.mozdns.mx.models import MX
from cyder.mozdns.mx.forms import MXForm
from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.views import MozdnsUpdateView


class MXView(object):
    """Group together common attributes."""
    model = MX
    form_class = MXForm
    queryset = MX.objects.all()


class MXDeleteView(MXView, MozdnsDeleteView):
    """ """


class MXDetailView(MXView, MozdnsDetailView):
    """ """
    template_name = 'mx/mx_detail.html'


class MXCreateView(MXView, MozdnsCreateView):
    """ """


class MXUpdateView(MXView, MozdnsUpdateView):
    """ """


class MXListView(MXView, MozdnsListView):
    """ """
