# Generated by Django 2.0.13 on 2020-07-27 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0009_auto_20200727_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='expense_type',
            field=models.CharField(choices=[('1', 'Seed'), ('2', 'Fertilizer'), ('3', 'Pesticides'), ('4', 'Water'), ('5', 'Electricity_bill'), ('6', 'Oil'), ('7', 'Labour'), ('9', 'Lease'), ('8', 'Miscellaneous')], max_length=255, verbose_name='Expense type'),
        ),
        migrations.AlterField(
            model_name='field',
            name='landlord_name',
            field=models.CharField(blank=True, help_text='Landlord name if not owned.', max_length=550, verbose_name='Landlord Name'),
        ),
        migrations.AlterField(
            model_name='field',
            name='landlord_number',
            field=models.CharField(blank=True, help_text='Landlord number if not owned.', max_length=550, verbose_name='Landlord Number'),
        ),
        migrations.AlterField(
            model_name='field',
            name='lease_end',
            field=models.DateField(blank=True, help_text='Lease end date if not owned.', null=True, verbose_name='Lease end'),
        ),
        migrations.AlterField(
            model_name='field',
            name='lease_per_acre',
            field=models.FloatField(blank=True, help_text='If leased then lease amount.', null=True, verbose_name='Lease per acre'),
        ),
        migrations.AlterField(
            model_name='field',
            name='lease_start',
            field=models.DateField(blank=True, help_text='Lease start date if not owned.', null=True, verbose_name='Lease start'),
        ),
    ]
