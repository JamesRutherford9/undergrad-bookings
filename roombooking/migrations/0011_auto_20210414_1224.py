# Generated by Django 3.1.7 on 2021-04-14 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roombooking', '0010_auto_20210414_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='length',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='booking',
            name='startTime',
            field=models.IntegerField(default=0),
        ),
    ]
