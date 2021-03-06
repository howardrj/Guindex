# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-12 20:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('TelegramUser', '0001_initial'),
        ('Guindex', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('UserProfile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='telegramuser',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='TelegramUser.TelegramUser'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
