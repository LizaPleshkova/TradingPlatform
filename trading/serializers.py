from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, OfferCnoice, UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('code', 'name', 'currency')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        exclude = ('name',)


class CurrencyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('code', 'name',)


class OfferListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        exclude = ('price', 'quantity', 'is_active')


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

    def validate(self, data):
        """ checking quantity seller's stocks """
        try:
            if data.get('type_transaction') == OfferCnoice.SELL.name:
                inventory_seller = Inventory.objects.get(user=data.get('user'),
                                                         item=data.get('item'))

                if inventory_seller.quantity <= data.get('quantity'):
                    raise serializers.ValidationError(('You want to sell more stocks than you have'), code='invalid')
            if data.get('type_transaction') == OfferCnoice.BUY.name:
                buyer_profile = UserProfile.objects.get(user=data.get('user'))
                if buyer_profile.score <= (data.get('quantity') * data.get('price')):
                    raise serializers.ValidationError(
                        ("There aren't enough cash in the account to buy such a quantity of dtocks"), code='invalid')
            return data
        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist('No Inventory seller matches the given query')


class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = ('item',)


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        exclude = ('quantity',)


class InventoryDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = Inventory
        fields = '__all__'


class PriceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        exclude = ('date', 'currency',)


class TradeSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField()
    buyer = serializers.StringRelatedField()

    class Meta:
        model = Trade
        fields = ('description', 'seller', 'buyer')


class TradeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'
