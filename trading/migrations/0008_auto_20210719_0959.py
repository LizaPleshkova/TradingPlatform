# Generated by Django 3.2.5 on 2021-07-19 09:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trading', '0007_alter_price_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='currency_item', to='trading.currency'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_offer', to='trading.item'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='type_transaction',
            field=models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=5, null=True, verbose_name='Type of transaction'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_offer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='price',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='currency_price', to='trading.currency'),
        ),
        migrations.AlterField(
            model_name='price',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_price', to='trading.item'),
        ),
        migrations.AlterField(
            model_name='watchlist',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_watchlist', to='trading.item'),
        ),
        migrations.AlterField(
            model_name='watchlist',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
