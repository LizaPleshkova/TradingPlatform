from rest_framework import serializers
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory


# Пользователь может создавать Offer на покупку или продажу указывая количество и стоимость.

class OfferListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        # field = ('item', 'user', 'price', 'quantity')
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'
