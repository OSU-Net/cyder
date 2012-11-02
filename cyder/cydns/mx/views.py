from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import cydns_list_create_record
from cyder.cydns.views import CydnsUpdateView


class MXView(object):
    """Group together common attributes."""
    model = MX
    form_class = MXForm
    queryset = MX.objects.all()


class MXDeleteView(MXView, CydnsDeleteView):
    """ """


class MXDetailView(MXView, CydnsDetailView):
    """ """
    template_name = 'mx/mx_detail.html'


class MXCreateView(MXView, CydnsCreateView):
    """ """


class MXUpdateView(MXView, CydnsUpdateView):
    """ """
