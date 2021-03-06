# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-14 13:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0002_auto_20180113_1009'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GuindexUser',
        ),
        migrations.AlterField(
            model_name='pub',
            name='pendingClosedContributor',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pendingCloser', to='UserProfile.UserProfile'),
        ),
        migrations.AlterField(
            model_name='pub',
            name='pendingNotServingGuinnessContributor',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pendingNotServingGuinnessMarker', to='UserProfile.UserProfile'),
        ),
    ]
