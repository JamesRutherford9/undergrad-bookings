# Generated by Django 3.1.7 on 2021-03-31 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roombooking', '0003_extra_extra_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=100),
        ),
    ]
