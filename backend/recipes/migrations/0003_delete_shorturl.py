# Generated by Django 4.2.16 on 2024-12-15 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_user_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ShortUrl',
        ),
    ]
