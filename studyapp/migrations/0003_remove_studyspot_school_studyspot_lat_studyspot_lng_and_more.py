# Generated by Django 4.2.6 on 2023-11-02 20:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studyapp', '0002_alter_review_published_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studyspot',
            name='school',
        ),
        migrations.AddField(
            model_name='studyspot',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='studyspot',
            name='lng',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='published_date',
            field=models.DateTimeField(verbose_name=datetime.datetime(2023, 11, 2, 20, 57, 36, 617335, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='studyspot',
            name='room_number',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
