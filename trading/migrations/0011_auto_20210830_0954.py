# Generated by Django 3.2.5 on 2021-08-30 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0010_auto_20210811_0940'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
            ],
        ),
        migrations.AddField(
            model_name='offer',
            name='counts_views',
            field=models.ManyToManyField(blank=True, related_name='offer_views', to='trading.Ip'),
        ),
    ]