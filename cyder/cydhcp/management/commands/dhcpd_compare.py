from django.core.management.base import BaseCommand, CommandError
from sys import stdout

from cyder.migration.management.commands.lib.dhcpd_compare.compare \
        import compare_files


class Command(BaseCommand):
    args = 'file1 file2'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('You must provide two files to compare')

        stdout.write(compare_files(args[0], args[1], verbose=True))
