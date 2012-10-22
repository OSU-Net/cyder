from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.views import MozdnsUpdateView


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
