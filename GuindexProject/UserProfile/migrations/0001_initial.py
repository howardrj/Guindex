# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-12 20:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountActivationKey', models.CharField(default=b'', max_length=12)),
                ('passwordResetToken', models.CharField(default=b'', max_length=12)),
                ('passwordResetTokenExpiry', models.DateTimeField(default=django.utils.timezone.now, max_length=40)),
                ('usingEmailAlerts', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfilePlugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
