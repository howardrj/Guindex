# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 09:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0005_auto_20180115_0923'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pub',
            old_name='pendingNotServigGuinnessTime',
            new_name='pendingNotServingGuinnessTime',
        ),
    ]