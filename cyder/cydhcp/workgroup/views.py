from cyder.cydhcp.workgroup.forms import WorkgroupForm
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue
from cyder.cydhcp.views import  *


class WorkgroupView(object):
    model = Workgroup
    form_class = WorkgroupForm
    queryset = Workgroup.objects.all()


class WorkgroupListView(WorkgroupView, CydhcpListView):
    """"""

class WorkgroupCreateView(WorkgroupView, CydhcpCreateView):
    """"""

class WorkgroupUpdateView(WorkgroupView, CydhcpUpdateView):
    """"""

class WorkgroupDetailView(WorkgroupView, CydhcpDetailView):
    """"""

class WorkgroupDeleteView(WorkgroupView, CydhcpDeleteView):
    """"""
