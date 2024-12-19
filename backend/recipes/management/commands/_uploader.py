import json

from django.core.management.base import BaseCommand


class UploaderBase(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        try:
            with open(options['path'], 'r', encoding='utf-8') as f:
                objects_count = self.model.objects.count()
                self.model.objects.bulk_create(
                    (self.model(**data) for data in json.load(f)),
                    ignore_conflicts=True
                )
                objects_count = self.model.objects.count() - objects_count
                self.stdout.write(
                    f'Новых записей: {objects_count}', ending='\n'
                )
        except OSError:
            self.stdout.write(
                f'Невозможно открыть файл {options["path"]}',
                ending='\n'
            )
        except Exception as err:
            self.stdout.write(
                str(err),
                ending='\n'
            )
