# Generated by Django 3.1.7 on 2021-04-14 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roombooking', '0009_auto_20210406_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='breakdownTime',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='setupTime',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AlterField(
            model_name='extrabookingmap',
            name='timing',
            field=models.TimeField(default='00:00'),
        ),
    ]
