import json

from django.core.management.base import BaseCommand


class UploaderBase(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        try:
            with open(options['path'], 'r', encoding='utf-8') as f:
                uploaded = self.model.objects.bulk_create(
                    (self.model(**data) for data in json.load(f)),
                    ignore_conflicts=True
                )
                self.stdout.write(
                    'Новых записей: {}'.format(len(uploaded)),
                    ending='\n'
                )
        except Exception as err:
            self.stdout.write(
                '\n'.join([
                    'Ошибка при чтении файла {}'.format(options['path']),
                    'Описание ошибки: {}'.format(str(err))
                ]),
                ending='\n'
            )
