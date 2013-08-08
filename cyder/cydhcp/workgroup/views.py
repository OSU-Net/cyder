import json

from django.shortcuts import get_object_or_404,  render
from django.http import HttpResponse, Http404

from cyder.base.utils import tablefy, make_paginator, make_megafilter
from cyder.cydhcp.workgroup.models import Workgroup


def workgroup_detail(request, workgroup_pk):
    workgroup = get_object_or_404(Workgroup, pk=workgroup_pk)
    attrs = workgroup.workgroupkeyvalue_set.all()
    static_hosts_paginator = make_paginator(
        request, workgroup.staticinterface_set.all(), record_type='static')
    dynamic_hosts_paginator = make_paginator(
        request, workgroup.dynamicinterface_set.all(), record_type='dynamic')
    return render(request, 'workgroup/workgroup_detail.html', {
        'object': workgroup,
        'workgroup_table': tablefy((workgroup,)),
        'dynamic_hosts_page_obj': dynamic_hosts_paginator,
        'dynamic_hosts_table': tablefy(dynamic_hosts_paginator),
        'static_hosts_page_obj': static_hosts_paginator,
        'static_hosts_table': tablefy(static_hosts_paginator),
        'attrs_table': tablefy(attrs),
    })


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
