# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-30 11:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0012_auto_20180130_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='pub',
            name='prices',
            field=models.ManyToManyField(related_name='prices', to='Guindex.Guinness'),
        ),
    ]
