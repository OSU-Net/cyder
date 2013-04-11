from itertools import chain, imap
import re


def parse_to_dict(*args, exclude_list = []):
    kwargs = {}
    for key, value in chain(*imap(lambda x: x.iteritems(), args)):
        if key in kwargs:
            kwargs[key].append(value)
        else:
            kwargs[key] = [value] if key not in exclude_from_list else value
    return kwargs

mac_match = "(([0-9a-f]){2}:){5}([0-9a-f]){2}$"
is_mac = re.compile(mac_match)
is_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
