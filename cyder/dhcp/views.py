from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
try:
    import json
except:
    from django.utils import simplejson as json
import _mysql_exceptions

import models
import forms
from cyder.truth.models import KeyValue as TruthKeyValue, Truth
from cyder.systems.models import NetworkAdapter
#import adapters.dhcp
from cyder.middleware.restrict_to_remote import allow_anyone

from DHCP import DHCP
from django.test.client import Client
from django.template.defaulttags import URLNode
from django.conf import settings
from jinja2.filters import contextfilter
from django.utils import translation


def showall(request):
    dhcp_scopes = models.DHCP.objects.all()
    import pdb
    pdb.set_trace()
    client = Client()
    resp = client.get('/en-US/api/keyvalue/?key=is_dhcp_scope', follow=True)
    obj = json.loads(resp.content)
    dhcp_scopes = []
    for key in obj.iterkeys():
        dhcp_scopes.append(key.split(":")[1])

    return render_to_response('dhcp/index.html', {
        'dhcp_scopes': dhcp_scopes,
    })


def new(request):
    error_message = ''
    if request.method == 'POST':
        form = forms.AddDHCPScopeForm(request.POST)
        if form.is_valid():
            truth_exists = False
            try:
                tmp = Truth.objects.get(name=form.cleaned_data['scope_name'])
                truth_exists = True
            except:
                pass
            if truth_exists is False:
                t = Truth(name=form.cleaned_data['scope_name'],
                          description=form.cleaned_data['scope_description'])
                t.save()
                k = TruthKeyValue(truth=t, key='is_dhcp_scope', value='True')
                k.save()
                return redirect('/dhcp/edit/%s' % t.name)
            else:
                error_message = 'DHCP Scope Exists'
    else:
        form = forms.AddDHCPScopeForm()

    return render_to_response('dhcp/new.html', {
        "form": form,
        "error_message": error_message
    })


def override_file(request, dhcp_scope):
    if request.method == 'POST':
        form = forms.DHCPScopeOverrideForm(request.POST)
        if form.is_valid():
            do = models.DHCPOverride.objects.get(dhcp_scope=dhcp_scope)
            do.override_text = form.cleaned_data['override_text']
            do.save()
            #s = form.save()
            #return redirect('/dhcp/show/')
    else:
        try:
            do = models.DHCPOverride.objects.get(dhcp_scope=dhcp_scope)
        except:
            do = models.DHCPOverride(dhcp_scope=dhcp_scope)
            do.save()

        form = forms.DHCPScopeOverrideForm(initial={'dhcp_scope': dhcp_scope,
                                           'override_text': do.override_text})

    return render_to_response('dhcp/override.html', {
        "form": form,
        'dhcp_scope': dhcp_scope
    },
        RequestContext(request))


def showfile(request, dhcp_scope):
    #scope = get_object_or_404(models.DHCP, pk=id)
    #truth = Truth.objects.get(name='phx-vlan73')
    #scope = TruthKeyValue(truth=truth)
    try:
        d = models.DHCPFile.objects.get(dhcp_scope=dhcp_scope)
        content = d.file_text
    except Exception, e:
        content = """This file has not been stored in inventory yet.
        To get it stored. Make an innocous change to a hosts key/value entry.
        An example would be to change the nic name from nic0 to nic1 then back to nic0 again and click save.
        Once the file gets regenerated, it will be stored here"""
    output = content.replace("\n", "<br />")
    return render_to_response('dhcp/showfile.html', {

        "output": output
    },
        RequestContext(request))


def create(request):
    if request.method == 'POST':
        form = forms.AddDHCPScopeForm(request.POST)
        if form.is_valid():
            pass
            #s = form.save()
            #return redirect('/dhcp/show/')
    else:
        form = forms.AddDHCPScopeForm()

    return render_to_response('dhcp/new.html', {
        "form": form
    },
        RequestContext(request))


def edit(request, dhcp_scope):
    client = Client()
    resp = client.get('/api/keyvalue/?keystore=%s' % dhcp_scope, follow=True)
    instance = json.loads(resp.content)
    initial = {}
    initial['scope_name'] = dhcp_scope
    ##A bunch of try/catch blocks to create key/value pairs if one does not exist
    try:
        initial['scope_start'] = instance['dhcp.scope.start']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.scope.start', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['scope_start'] = ''
    try:
        initial['scope_end'] = instance['dhcp.scope.end']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.scope.end', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['scope_end'] = ''
    try:
        initial['scope_netmask'] = instance['dhcp.scope.netmask']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.scope.netmask', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['scope_netmask'] = ''
    try:
        initial['pool_start'] = instance['dhcp.pool.start']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.pool.start', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['pool_start'] = ''
    try:
        initial['pool_end'] = instance['dhcp.pool.end']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.pool.end', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['pool_end'] = ''
    try:
        initial['ntp_server1'] = instance['dhcp.option.ntp_server.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.option.ntp_server.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['ntp_server1'] = ''
    try:
        initial['ntp_server2'] = instance['dhcp.option.ntp_server.1']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.option.ntp_server.1', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['ntp_server2'] = ''
    try:
        initial['router'] = instance['dhcp.option.router.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.option.router.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['router'] = ''
    try:
        initial['domain_name'] = instance['dhcp.option.domain_name.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.option.domain_name.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['domain_name'] = ''
    try:
        initial['dns_server1'] = instance['dhcp.dns_server.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.dns_server.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['dns_server1'] = ''
    try:
        initial['dns_server2'] = instance['dhcp.dns_server.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.dns_server.1', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['dns_server2'] = ''
    try:
        initial['allow_booting'] = instance['dhcp.pool.allow_booting.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.pool.allow_booting.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['allow_booting'] = ''
    try:
        initial['allow_bootp'] = instance['dhcp.pool.allow_bootp.0']
    except:
        client.post('/en-US/api/keyvalue/%s/' % dhcp_scope, {'key': 'dhcp.pool.allow_bootp.0', 'value': '', 'truth_name': dhcp_scope}, follow=True)
        initial['allow_bootp'] = ''

    if request.method == 'POST':
        form = forms.EditDHCPScopeForm(request.POST)
        if form.is_valid():
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.scope.start', 'value': form.cleaned_data['scope_start']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.scope.end', 'value': form.cleaned_data['scope_end']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.scope.netmask', 'value': form.cleaned_data['scope_netmask']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.pool.start', 'value': form.cleaned_data['pool_start']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.pool.end', 'value': form.cleaned_data['pool_end']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.option.ntp_server.0', 'value': form.cleaned_data['ntp_server1']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.option.ntp_server.1', 'value': form.cleaned_data['ntp_server2']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.dns_server.0', 'value': form.cleaned_data['dns_server1']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.dns_server.1', 'value': form.cleaned_data['dns_server2']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.option.domain_name.0', 'value': form.cleaned_data['domain_name']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.option.router.0', 'value': form.cleaned_data['router']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.pool.allow_booting.0', 'value': form.cleaned_data['allow_booting']}, follow=True)
            client.put('/en-US/api/v2/keyvalue/%s/' % dhcp_scope, {'truth_id': dhcp_scope, 'key': 'dhcp.pool.allow_bootp.0', 'value': form.cleaned_data['allow_bootp']}, follow=True)
    else:
        form = forms.EditDHCPScopeForm(initial=initial)

    return render_to_response('dhcp/edit.html', {
        "form": form,
        'dhcp_scope': dhcp_scope
    })


def delete(request, dhcp_scope):
    try:
        scope = Truth.objects.get(name=dhcp_scope)
        TruthKeyValue.objects.filter(truth=scope).delete()
        scope.delete()
        return redirect('/dhcp/show/')
    except:
        return redirect('/dhcp/show/')
