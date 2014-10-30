from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface

import json


def is_last_interface(request):
    obj_type = request.POST['obj_type']
    pk = request.POST['pk']
    Klass = get_model('cyder', obj_type.replace('_', ''))
    obj = get_object_or_404(Klass, pk=pk)
    last_interface = False
    if (len(DynamicInterface.objects.filter(system=obj.system))
            + len(StaticInterface.objects.filter(system=obj.system)) == 1):
        last_interface = True

    return HttpResponse(json.dumps({'last_interface': last_interface}))
