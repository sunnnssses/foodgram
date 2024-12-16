import json

from django.core.management.base import BaseCommand


class UploaderBase(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        try:
            f = open(options['path'], 'r', encoding='utf-8')
        except OSError:
            self.stdout.write(f'Невозможно открыть файл {options["path"]}',
                              ending='\n')
            return
        with f:
            self.model.objects.bulk_create(
                (self.model(**data) for data in json.load(f)),
                ignore_conflicts=True
            )
