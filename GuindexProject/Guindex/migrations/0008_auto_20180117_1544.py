# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-17 15:44
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0007_auto_20180117_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guinness',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
