from cyder.cydns.nameserver.forms import Nameserver, NameserverForm,
from cyder.cydns.views import cy_render


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()
    extra_context = {'obj_type': 'nameserver'}
