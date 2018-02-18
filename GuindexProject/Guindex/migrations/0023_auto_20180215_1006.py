# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-15 10:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0022_auto_20180215_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='guinness',
            name='hasPendingContribution',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='guinness',
            name='rejectReason',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='pub',
            name='creationDate',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pub',
            name='hasPendingContribution',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pub',
            name='rejectReason',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
