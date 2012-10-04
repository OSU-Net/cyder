from piston.handler import BaseHandler, rc
from cyder.systems.models import System, SystemRack, SystemStatus, NetworkAdapter, KeyValue, ScheduledTask
from cyder.truth.models import Truth, KeyValue as TruthKeyValue
from cyder.dhcp.DHCP import DHCP as DHCPInterface
from cyder.dhcp.models import DHCP
from MacroExpansion import MacroExpansion
from KeyValueTree import KeyValueTree
import re
try:
    import json
except:
    from django.utils import simplejson as json
from django.test.client import Client
from django.conf import settings


class DHCPHandler(BaseHandler):
    allowed_methods = settings.API_ACCESS
    model = System
    #fields = ('id', 'asset_tag', 'oob_ip', 'hostname', 'operating_system', ('system_status',('status', 'id')))
    exclude = ()

    def read(self, request, dhcp_scope=None, dhcp_action=None):
        if dhcp_scope and dhcp_action == 'get_scopes':
            tasks = []
            for task in ScheduledTask.objects.get_all_dhcp():
                tasks.append(task.task)
            ScheduledTask.objects.delete_all_dhcp()
            return tasks
        if dhcp_scope and dhcp_action == 'get_scopes_with_names':
            truths = Truth.objects.select_related().filter(
                keyvalue__key='is_dhcp_scope', keyvalue__value='True')

            truth_list = []
            for t in truths:
                truth_list.append({'name': t.name.strip(
                ), 'description': t.description.strip()})
            return truth_list
        if dhcp_scope and dhcp_action == 'view_hosts':
            scope_options = []
            client = Client()
            hosts = json.loads(client.get('/api/keyvalue/?key_type=system_by_scope&scope=%s' % dhcp_scope).content)
            #print hosts
            adapter_list = []
            for host in hosts:
                if 'hostname' in host:
                    the_url = '/api/keyvalue/?key_type=adapters_by_system_and_scope&dhcp_scope=%s&system=%s' % (dhcp_scope, host['hostname'])
                    try:
                        adapter_list.append(
                            json.loads(client.get(the_url).content))
                    except:
                        pass
            d = DHCPInterface(scope_options, adapter_list)
            return d.get_hosts()
