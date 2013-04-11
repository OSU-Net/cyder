from itertools import chain
import re


def parse_to_object(parse, Klass, exclude_from_list = []):
    kwargs = {}
    for key, value in chain(*(elem.items() for elem in parse)):
        if key in kwargs:
            kwargs[key].append(value)
        else:
            kwargs[key] = [value] if key not in exclude_from_list else value
    return Klass(**kwargs)


mac_match = "(([0-9a-f]){2}:){5}([0-9a-f]){2}$"
is_mac = re.compile(mac_match)
is_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
