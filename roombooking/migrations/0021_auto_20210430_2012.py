# Generated by Django 3.1.7 on 2021-04-30 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roombooking', '0020_auto_20210428_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='extra',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]