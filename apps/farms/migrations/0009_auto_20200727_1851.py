# Generated by Django 2.0.13 on 2020-07-27 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0008_auto_20200727_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='lease_per_acre',
            field=models.FloatField(blank=True, help_text='If leased then lease amount', null=True, verbose_name='Lease per acre'),
        ),
    ]
