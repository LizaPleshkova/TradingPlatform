# Generated by Django 3.2.5 on 2021-09-06 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0014_auto_20210902_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stripe_client_id',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]