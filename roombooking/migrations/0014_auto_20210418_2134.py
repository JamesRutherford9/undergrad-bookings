# Generated by Django 3.1.7 on 2021-04-18 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roombooking', '0013_auto_20210415_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='length',
            field=models.IntegerField(choices=[(0, '0:30'), (1, '1:00'), (2, '1:30'), (3, '2:00'), (4, '2:30'), (5, '3:00'), (6, '3:30'), (7, '4:00'), (8, '4:30'), (9, '5:00'), (10, '5:30'), (11, '6:00'), (12, '6:30'), (13, '7:00'), (14, '7:30'), (15, '8:00'), (16, '8:30'), (17, '9:00'), (18, '9:30'), (19, '10:00')], default=0),
        ),
    ]
