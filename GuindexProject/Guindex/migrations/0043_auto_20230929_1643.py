# Generated by Django 2.2.28 on 2023-09-29 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0042_auto_20230929_1642'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pubpendingpatch',
            old_name='clonedFrom',
            new_name='cloned_from',
        ),
    ]