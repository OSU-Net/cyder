import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404

from cyder.base.utils import make_megafilter
from cyder.base.views import cy_detail
from cyder.cydhcp.workgroup.models import Workgroup


def workgroup_detail(request, pk):
    workgroup = get_object_or_404(Workgroup, pk=pk)
    return cy_detail(request, Workgroup, 'workgroup/workgroup_detail.html', {
        'Attributes': 'workgroupav_set',
        'Dynamic Interfaces': workgroup.dynamicinterface_set.all(),
        'Static Interfaces': workgroup.staticinterface_set.all(),
    }, obj=workgroup)


def search(request):
    """Returns a list of workgroups matching 'term'."""
    term = request.GET.get('term', '')
    if not term:
        raise Http404

    workgroups = Workgroup.objects.filter(
        make_megafilter(Workgroup, term))[:15]
    workgroups = [{
        'label': str(workgroup),
        'pk': workgroup.id} for workgroup in workgroups]
    return HttpResponse(json.dumps(workgroups))
