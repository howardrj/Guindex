# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-08 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0019_guinness_rejectreason'),
    ]

    operations = [
        migrations.AddField(
            model_name='pub',
            name='pendingApprovalRejectReason',
            field=models.TextField(default=None, null=True),
        ),
    ]
