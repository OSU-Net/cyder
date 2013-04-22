from itertools import chain, imap, groupby
import re
from dhcp_objects import (Option, Group, Host, Parameter, Pool, Allow,
                          Deny, Subnet, )

key_table = [(Option, 'options'),
             (Group, 'groups'),
             (Host, 'hosts'),
             (Parameter, 'parameters'),
             (Pool, 'pools'),
             (Allow, 'allow'),
             (Deny, 'deny'),
             (Subnet, 'subnets'),
             ('mac', 'mac'),
             ('start', 'start'),
             ('end', 'end'),
             ('fqdn', 'fqdn'),
             ('match' , 'match')]


def get_key(obj):
    for o, k in key_table:
        if obj is o:
            return k
    raise Exception("key {0} was not found".format(obj))


def prepare_arguments(attrs, exclude_list=None, **kwargs):
    exclude_list = exclude_list or []
    new_kwargs = {}
    dicts = [d for d in attrs if type(d) is dict]
    kwargs.update(dict(chain(*map(lambda x: x.items(), dicts))))
    attrs = [a for a in attrs if not (type(a) is dict)]
    for k, g in groupby(sorted(attrs, key=type), type):
        key = get_key(k)
        kwargs[key] = list(g) if not key in exclude_list else list(g)[0]
    return dict(new_kwargs.items() + kwargs.items())


mac_match = "(([0-9a-fA-F]){2}:){5}([0-9a-fA-F]){2}$"
is_mac = re.compile(mac_match)
is_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
