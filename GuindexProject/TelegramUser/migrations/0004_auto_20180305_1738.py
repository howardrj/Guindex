# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-05 17:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('TelegramUser', '0003_auto_20180220_1729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramuser',
            name='userProfile',
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='user',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telegramuser', to=settings.AUTH_USER_MODEL),
        ),
    ]
