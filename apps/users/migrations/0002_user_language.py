# Generated by Django 3.0.8 on 2020-07-25 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('ur', 'Urdu')], default='en', max_length=2),
        ),
    ]