# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-27 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0031_auto_20180525_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='guindexuser',
            name='isDeveloper',
            field=models.BooleanField(default=False),
        ),
    ]
