from string import hexdigits

GLOBAL = 0
SUBNET = 1
POOL = 2
CLASS = 3
GROUP = 4
HOST = 5

keywords = ['deny', 'class', 'subclass', 'option', 'range', 'match',
            'fixed-address', 'hardware ethernet', 'host', 'subnet', 'allow',
            'pool', 'group']

reserved_chars = [';', '}', '{']
