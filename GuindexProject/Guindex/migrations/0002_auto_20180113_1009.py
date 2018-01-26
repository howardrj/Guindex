# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-13 10:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0002_auto_20180112_2059'),
        ('Guindex', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pub',
            name='approved',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingClosed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingClosedContributor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pendingCloser', to='UserProfile.UserProfile'),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingClosedTime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingNotServigGuinnessTime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingNotServingGuinness',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pub',
            name='pendingNotServingGuinnessContributor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pendingNotServingGuinnessMarker', to='UserProfile.UserProfile'),
        ),
    ]
