# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-14 21:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0002_auto_20171214_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guinness',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserProfile.UserProfile'),
        ),
        migrations.AlterField(
            model_name='pub',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserProfile.UserProfile'),
        ),
    ]