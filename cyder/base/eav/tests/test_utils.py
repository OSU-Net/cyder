from django.core.exceptions import ValidationError
from django.test import TestCase

from cyder.base.eav import utils as u


class TestUtils(TestCase):
    def _valid(self, func, value_list):
        for value in value_list:
            self.assertTrue(func(value))


    def _invalid(self, func, value_list):
        for value in value_list:
            self.assertFalse(func(value))


    def test_is_hex_byte(self):
        self._valid(u.is_hex_byte, ('01', '23', '45', '67', '89', 'ab', 'cd',
                                    'ef', 'AB', 'CD', 'EF'))
        self._invalid(u.is_hex_byte, (
            '012', # too many digits
            'no', # invalid byte
            '0x01', # '0x' not allowed (we already know it's hex)
            '-1a', # negative bytes not allowed
        ))

    def test_is_hex_byte_sequence(self):
        self._valid(u.is_hex_byte_sequence, ('01', '01:23:45:67:89:ab:cd:ef'))
        self._invalid(u.is_hex_byte_sequence, (
            '012:34', # invalid byte
            '01::23', # too many consecutive colons
            '01:', # trailing colon
            ':01', # leading colon
            'yes:no', # invalid bytes
        ))
