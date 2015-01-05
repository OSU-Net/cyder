from django.core.exceptions import ValidationError
from django.test import TestCase

from cyder.base.eav import utils


class TestUtils(TestCase):
    def test_is_hex_byte(self):
        good_values = (
            '01', '23', '45', '67', '89', 'ab', 'cd',
            'ef', 'AB', 'CD', 'EF')
        for value in good_values:
            self.assertTrue(utils.is_hex_byte(value))

        bad_values = (
            '012',  # too many digits
            'no',  # invalid byte
            '0x01',  # '0x' not allowed (we already know it's hex)
            '-1a',  # negative bytes not allowed
        )
        for value in bad_values:
            self.assertFalse(utils.is_hex_byte(value))

    def test_is_hex_byte_sequence(self):
        good_values = ('01', '01:23:45:67:89:ab:cd:ef')
        for value in good_values:
            self.assertTrue(utils.is_hex_byte_sequence(value))

        bad_values = (
            '012:34',  # invalid byte
            '01::23',  # too many consecutive colons
            '01:',  # trailing colon
            ':01',  # leading colon
            'yes:no',  # invalid bytes
        )
        for value in bad_values:
            self.assertFalse(utils.is_hex_byte_sequence(value))
