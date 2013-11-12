import ipaddr

from django import forms
from django.forms.util import ErrorDict, ErrorList
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models.loading import get_model

from cyder.base.utils import tablefy, qd_to_py_dict
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
        related_systems.update(intr.get_related_systems())
        static_intr.append((tablefy((intr,), request=request),
                            tablefy(intr.staticinterfaceav_set.all(),
                                    request=request)))
    for intr in dynamic:
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


def system_create_view(request, initial):
    static_form = StaticInterfaceForm()
    dynamic_form = DynamicInterfaceForm()
    system_form = ExtendedSystemForm()

    if request.POST:
        post_data = qd_to_py_dict(request.POST)
        if not post_data['ctnr']:
            post_data['ctnr'] = request.session['ctnr'].id
        system_data = {}
        initial = post_data.pop('initial', None)
        system_data['name'] = post_data.pop('name', None)
        system_data['interface_type'] = post_data.pop('interface_type', None)
        system_form = ExtendedSystemForm(system_data)

        if system_form.is_valid():
            system = system_form.save()
            post_data['system'] = system.id

        else:
            system = None

        if system_data.get('interface_type', '') is None:
            if system:
                system.delete()

        else:
            if system_data.get('interface_type', '') == 'Static':
                form = StaticInterfaceForm(post_data)
                static_form = form
            elif system_data.get('interface_type', '') == 'Dynamic':
                form = DynamicInterfaceForm(post_data)
                dynamic_form = form

            if form.is_valid():
                try:
                    form.save()
                    return redirect(reverse('system-detail', args=[system.id]))
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

    if initial == 'static_interface':
        interface_type = 'Static'

    elif 'dynamic_interface' in initial:
        interface_type = 'Dynamic'
        if 'range_' in initial:
            pk = initial.split('range_')[1]
            Range = get_model('cyder', 'range')
            rng = Range.objects.filter(pk=pk)
            if rng.exists():
                dynamic_form.fields['range'].initial = rng[0]
            dynamic_form.fields['range'].queryset = rng
            dynamic_form.fields['range'].empty_label = None

    else:
        try:
            ipaddr.IPAddress(initial)
            ip_type = ipaddr.IPAddress(initial).version
            interface_type = 'Static'
            static_form.initial = dict({'ip_str': initial, 'ip_type': ip_type})
            for field in ['vrf', 'site', 'range', 'next_ip']:
                static_form.fields[field].widget = forms.HiddenInput()

            static_form.fields['ip_str'].widget.attrs['readonly'] = True
            static_form.fields['ip_type'].widget.attrs['readonly'] = True
            static_form.fields['ip_type'].choices = [
                (str(ip_type), "IPv{0}".format(ip_type))]

        except ValueError:
            interface_type = None

    if interface_type:
        system_form.fields['interface_type'].initial = interface_type
        system_form.fields['interface_type'].widget.attrs['readonly'] = True
        system_form.fields['interface_type'].choices = [
            (str(interface_type), "{0} Interface".format(interface_type))]

    static_form.fields['system'].widget = forms.HiddenInput()
    dynamic_form.fields['system'].widget = forms.HiddenInput()

    if request.session['ctnr'].name != 'global':
        dynamic_form.fields['ctnr'].widget = forms.HiddenInput()
        static_form.fields['ctnr'].widget = forms.HiddenInput()

    system_form.make_usable(request)
    static_form.make_usable(request)
    dynamic_form.make_usable(request)

    return render(request, 'system/system_create.html', {
        'system_form': system_form,
        'static_form': static_form,
        'dynamic_form': dynamic_form,
        'initial': initial})
