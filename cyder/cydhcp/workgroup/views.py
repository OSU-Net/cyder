from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.workgroup.models import Workgroup


def workgroup_detail(request, pk):
    workgroup = get_object_or_404(Workgroup, pk=pk)
    return cy_detail(request, Workgroup, 'workgroup/workgroup_detail.html', {
        'Attributes': 'workgroupkeyvalue_set',
        'Dynamic Interfaces': workgroup.dynamicinterface_set.all(),
        'Static Interfaces': workgroup.staticinterface_set.all(),
    }, obj=workgroup)
