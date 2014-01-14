import ipaddr
from copy import copy

from django import forms
from django.forms.util import ErrorDict, ErrorList
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from cyder.base.utils import tablefy
from cyder.core.system.models import System
from cyder.core.system.forms import ExtendedSystemForm
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.cydhcp.validation import MAC_ERR


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
        'system_table': tablefy([system], info=False, request=request),
        'attrs_table': tablefy(attrs, request=request),
        'static_intr_tables': static_intr,
        'dynamic_intr_tables': dynamic_intr,
        'related_systems_table': tablefy(list(related_systems),
                                         request=request),
        'obj_type': 'system',
        'obj': system,
    })


def system_create_view(request):
    static_form = StaticInterfaceForm()
    dynamic_form = DynamicInterfaceForm()
    system_form = ExtendedSystemForm()
    if request.POST:
        system = None
        post_data = copy(request.POST)
        if not post_data.get('ctnr'):
            post_data['ctnr'] = request.session['ctnr'].id

        system_form = ExtendedSystemForm(post_data)
        if system_form.is_valid():
            system = system_form.save(commit=False)
        if post_data.get('interface_type', '') is not None:
            if system:
                system.save()
                post_data['system'] = system.id

            if post_data.get('interface_type', None) == 'Static':
                try:
                    post_data['ip_type'] = ipaddr.IPAddress(
                        post_data.get('ip_str', None)).version
                except:
                    post_data['ip_type'] = None

                form = StaticInterfaceForm(post_data)
                static_form = form
            elif post_data.get('interface_type', None) == 'Dynamic':
                form = DynamicInterfaceForm(post_data)
                dynamic_form = form

            if form.is_valid():
                try:
                    form.save()
                    return redirect(
                        reverse('system-detail', args=[system.id]))
                except ValidationError, e:
                    form._errors = ErrorDict()
                    form._errors['__all__'] = ErrorList(e.messages)
            else:
                if '__all__' in form.errors and (
                        MAC_ERR in form.errors['__all__']):
                    form.errors['__all__'].remove(MAC_ERR)
                    if 'mac' not in form.errors:
                        form.errors['mac'] = []
                    if MAC_ERR not in form.errors['mac']:
                        form.errors['mac'].append(MAC_ERR)

                if system:
                    system.delete()

            if request.POST.get('initial', None):
                system_form.errors.clear()
                static_form.errors.clear()
                dynamic_form.errors.clear()

    static_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['system'].widget = forms.HiddenInput()
    static_form.fields['ip_type'].widget = forms.HiddenInput()

    if request.session['ctnr'].name != 'global':
        dynamic_form.fields['ctnr'].widget = forms.HiddenInput()
        static_form.fields['ctnr'].widget = forms.HiddenInput()

    system_form.make_usable(request)
    static_form.make_usable(request)
    dynamic_form.make_usable(request)
    return render(request, 'system/system_create.html', {
        'system_form': system_form,
        'static_form': static_form,
        'dynamic_form': dynamic_form})
