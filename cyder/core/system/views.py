from django.shortcuts import render

from cyder.base.utils import make_paginator, tablefy
from cyder.core.system.models import System


def systems(request):
    object_list = make_paginator(request, System.objects.all(), 50)
    return render(request, 'system/systems.html', {
        'object_list': object_list,
        'object_table': tablefy(object_list)
    })
