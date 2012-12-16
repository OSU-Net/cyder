from cyder.core.views import CoreListView
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System


class SystemView(object):
    model = System
    form_class = SystemForm


class SystemListView(SystemView, CoreListView):
    """"""
