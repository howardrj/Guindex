# Generated by Django 2.2.28 on 2023-09-29 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Guindex', '0041_auto_20230929_1641'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pub',
            old_name='averageRating',
            new_name='average_rating',
        ),
        migrations.RenameField(
            model_name='pub',
            old_name='lastPrice',
            new_name='last_price',
        ),
        migrations.RenameField(
            model_name='pub',
            old_name='lastSubmissionTime',
            new_name='last_submission_time',
        ),
    ]