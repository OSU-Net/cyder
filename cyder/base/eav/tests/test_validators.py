from django.core.exceptions import ValidationError
from django.test import TestCase

from cyder.base.eav import validators as v


class TestValidators(TestCase):
    def _valid(self, validator, value_list):
        for value in value_list:
            validator(value)

    def _invalid(self, validator, value_list):
        for value in value_list:
            self.assertRaises(ValidationError, lambda: validator(value))

    def test_flag(self):
        self._valid(v.flag, ('on', 'off', 'true', 'false', 'oN', 'True'))
        self._invalid(v.flag, ('truth', 'yes', 'no', '0', '1'))

    def test_uint8(self):
        self._valid(v.uint8, ('0', '10', '255', '0x0', '0xa', '0xFF'))
        self._invalid(v.uint8, ('-1', 'a', '256', '-0x1', '0x-1', '0x100'))

    def test_int8(self):
        self._valid(
            v.int8, ('-128', '-10', '0', '10', '127', '0x0', '0xa', '0x7F'))
        self._invalid(v.int8, ('-129', '1a', '128'))

    def test_domain(self):
        self._valid(v.domain, ('com', 'example.com', 'example.com.'))
        self._invalid(v.domain, (
            '.com',  # missing label
            'example.com..',  # too many dots
            'example..com',  # too many dots
        ))

    def test_host(self):
        self._valid(v.host, (
            'foo', 'example.com', 'example.com.', '1.2.3.4', '127.0.0.1',
        ))
        self._invalid(v.host, (
            '.com',  # missing label
            'example.com..',  # too many dots
            'example..com',  # too many dots
        ))

    def test_domain_list(self):
        self._valid(v.domain_list, (
            '"example.com"',
            '"example.com", "example.org." ,"example.edu"',
        ))
        self._invalid(v.domain_list, (
            'example.com',  # no quotes
            '"example.com" "example.org."  "example.edu"',  # no commas
        ))

    def test_host_pair(self):
        self._valid(v.host_pair, (
            'example.com example.org',
            '1.2.3.4 example.com',
            'example.com     1.2.3.4',  # multiple spaces
            '1.2.3.4 127.0.0.1',
        ))
        self._invalid(v.host_pair, (
            'example.com, example.org',  # comma
            'example..com example.org',  # invalid host
            'example.com',  # too few hosts
            '1.2.3.4 127.0.0.1 192.168.0.1',  # too many hosts
        ))

    def test_host_pair_list(self):
        self._valid(v.host_pair_list, (
            'example.com example.org',
            'example.com example.org, example.edu example.net',
            '1.2.3.4 127.0.0.1, 10.0.0.1 192.168.0.1',
            'example.com 1.2.3.4, example.org 127.0.0.1',
        ))
        self._invalid(v.host_pair_list, (
            'example.com',  # too few hosts in a pair
            'example.com, example.org example.edu',  # too few hosts in a pair
            '1.2.3.4 127.0.0.1 192.168.0.1',  # too many hosts in a pair
        ))

    def test_flag_host_list(self):
        self._valid(v.flag_host_list, (
            'true example.com, example.org',
            'false example.com, example.org, 127.0.0.1',
            'on 127.0.0.1',
        ))
        self._invalid(v.flag_host_list, (
            'true',  # no hosts
            'false example.com example.org',  # no space between hosts
            'yes, 127.0.0.1',  # comma after flag
        ))

    def test_text(self):
        self._valid(v.text, (
            'foo', 'foo bar', "'foo bar'", '!@#$%^&*()_',
            # hex byte sequence in text is valid but not special
            '3A:B0', 'DE:AD:be:ef',
        ))
        self._invalid(v.text, (
            '"foo"',  # double quote
            'foo"bar',  # double quote
        ))

    def test_string(self):
        self._valid(v.string, (
            'foo', 'foo bar', 'foo bar baz', "'foo bar baz'",
            # hex byte sequence in string is valid and special
            '3A:B0', 'DE:AD:be:ef',
        ))
        self._invalid(v.string, (
            '"foo"',  # double quotes
            'foo"bar',  # double quote
        ))

    def test_identifier(self):
        self._valid(v.identifier, (
            'f', 'foobar', 'FooBar', 'Foo_Bar_', 'Foo-Bar-', 'foo9bar',
            '9foobar', 'foobar9',
            '9-9', '9_9',  # don't ask
        ))
        self._invalid(v.identifier, (
            '99',  # all digits
            'foo:bar',  # ':'
            '"foobar"',  # double quote
            "'foobar",  # single quote
        ))

    def test_flag_optional_text(self):
        self._valid(v.flag_optional_text, (
            'true',
            'off',
            'true "foobar"',
            'false "foo bar"',
            'On "!@#$%^&*_"',
        ))
        self._invalid(v.flag_optional_text, (
            'truth',  # invalid flag
            'true foobar',  # no quotes around text
            'false, "foobar"',  # comma between flag and text
        ))
