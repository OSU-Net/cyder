from django.core.exceptions import ValidationError
from django.forms.util import ErrorList, ErrorDict

from cyder.cydhcp.keyvalue.utils import get_attrs, update_attrs
from cyder.cydhcp.views import CydhcpCreateView
from cyder.cydhcp.vrf.forms import VrfForm
from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue


class VrfView(object):
    model = Vrf
    queryset = Vrf.objects.all()
    form_class = VrfForm

class VrfCreateView(VrfView, CydhcpCreateView):
    """"""
