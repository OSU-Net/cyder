import ipaddr
import simplejson as json
from copy import copy

from django import forms
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models import get_model
from django.forms.util import ErrorDict, ErrorList
from django.http import HttpResponse
from django.shortcuts import render, redirect

from cyder.base.utils import tablefy
from cyder.core.system.models import System
from cyder.core.system.forms import ExtendedSystemForm
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.base.tablefier import Tablefier

def system_detail(request, pk):
    try:
        system = System.objects.get(id=pk)
    except:
        return redirect(reverse('system'))

    attrs = system.systemav_set.all()
    dynamic = DynamicInterface.objects.filter(system=system)
    related_systems = set()

    static = StaticInterface.objects.filter(system=system)
    static_intr = []
    dynamic_intr = []
    for intr in static:
        if intr.mac:
            related_systems.update(intr.get_related_systems())
        static_intr.append((tablefy((intr,), request=request),
                            tablefy(intr.staticinterfaceav_set.all(),
                                    request=request)))
    for intr in dynamic:
        if intr.mac:
            related_systems.update(intr.get_related_systems())
        dynamic_intr.append((tablefy((intr,), request=request),
                             tablefy(intr.dynamicinterfaceav_set.all(),
                                     request=request)))

    related_systems.discard(system)

    return render(request, 'system/system_detail.html', {
        'attrs_table': tablefy(attrs, request=request),
        'static_intr_tables': static_intr,
        'dynamic_intr_tables': dynamic_intr,
        'related_systems_table': tablefy(list(related_systems),
                                         request=request),
        'obj_type': 'system',
        'obj': system,
        'pretty_obj_type': system.pretty_type,
    })

def validate_system_create_form(request):
    system = None
    post_data = copy(request.POST)
    if not post_data.get('ctnr'):
        post_data['ctnr'] = request.session['ctnr'].id

    system_form = ExtendedSystemForm(post_data)
    if system_form.is_valid():
        system = system_form.save()
        post_data['system'] = system.id
    else:
        return HttpResponse(json.dumps({'errors': system_form.errors}))

    if post_data.get('interface_type', None) == 'static_interface':
        try:
            post_data['ip_type'] = ipaddr.IPAddress(
                post_data.get('ip_str', None)).version
        except:
            post_data['ip_type'] = None

        form = StaticInterfaceForm(post_data)
    else:
        form = DynamicInterfaceForm(post_data)

    if form.is_valid():
        try:
            form.save()
            return HttpResponse(json.dumps(
                {'success': True, 'system_id': system.id}))
        except ValidationError as e:
            if form.errors is None:
                form.errors = ErrorDict()
            form.errors.update(e.message_dict)
            return HttpResponse(json.dumps({'errors': form.errors}))
    else:
        if system:
            system.delete()

        return HttpResponse(json.dumps({'errors': form.errors}))


def system_create_view(request):
    if request.method == 'POST':
        return validate_system_create_form(request)

    initial_type = None
    static_form = StaticInterfaceForm()
    dynamic_form = DynamicInterfaceForm()
    system_form = ExtendedSystemForm()
    if(request.GET.get('initial', None)):
        initial_type = request.GET['interface_type']
        system_form = ExtendedSystemForm(
            initial={'interface_type': initial_type})
        system_form.fields['interface_type'].widget = forms.HiddenInput()
        if request.GET.get('ip_str', None):
            static_form = StaticInterfaceForm(
                initial={'ip_str': request.GET['ip_str']})
            static_form.fields['range'].widget = forms.HiddenInput()
            static_form.fields['vrf'].widget = forms.HiddenInput()
            static_form.fields['site'].widget = forms.HiddenInput()
            static_form.fields['next_ip'].widget = forms.HiddenInput()
        elif request.GET.get('range', None):
            dynamic_form = DynamicInterfaceForm(
                initial={'range': request.GET['range']})
            dynamic_form.fields['vrf'].widget = forms.HiddenInput()
            dynamic_form.fields['site'].widget = forms.HiddenInput()

    Range = get_model('cyder', 'range')
    static_form.fields['system'].widget = forms.HiddenInput()
    static_form.fields['range'].queryset = Range.objects.filter(range_type='st')
    dynamic_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['range'].queryset = Range.objects.filter(range_type='dy')
    static_form.fields['ip_type'].widget = forms.HiddenInput()

    if request.session['ctnr'].name != 'global':
        dynamic_form.fields['ctnr'].widget = forms.HiddenInput()
        static_form.fields['ctnr'].widget = forms.HiddenInput()

    system_form.make_usable(request)

    static_form.make_usable(request)
    dynamic_form.make_usable(request)

    return HttpResponse(json.dumps({
        'form_title': 'Creating system',
        'submit_btn_label': 'Create system',
        'system_form': system_form.as_p(),
        'static_form': static_form.as_p(),
        'dynamic_form': dynamic_form.as_p(),
        'initial_type': initial_type}))
