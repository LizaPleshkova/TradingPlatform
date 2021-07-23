from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, OfferCnoice, UserProfile

User = get_user_model()



class OfferListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        exclude = ('price', 'quantity', 'is_active')


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
        fields = '__all__'


class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# <<<<<<< HEAD
# class OfferListSerializer(serializers.ModelSerializer):
#     ''' serializer for offer's list (method get) '''
#
#     class Meta:
#         model = Offer
#         exclude = ('price', 'quantity', 'is_active')
#

# class OfferDetailSerializer(serializers.ModelSerializer):
#     ''' serializer for offer's detail (method get/post)'''
#
#     user = UserSerializer()
#     item = ItemSerializer()

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # fields = ('code', 'name', 'description',)

        # exclude = ('code', 'currency',)


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'


    def validate(self, data):
        """ checking quantity seller's stocks """
        try:
            if data.get('type_transaction') == OfferCnoice.SELL.name:
                seller = inventory_seller = Inventory.objects.get(user=data.get('user'),
                                                                  item=data.get('item'))
                if inventory_seller.quantity < data.get('quantity'):
                    raise serializers.ValidationError(('You want to sell more stocks than you have'), code='invalid')
            if data.get('type_transaction') == OfferCnoice.BUY.name:
                buyer_profile = UserProfile.objects.get(user=data.get('user'))
                print(data.get('quantity') * data.get('price'))
                if buyer_profile.score <= (data.get('quantity') * data.get('price')):
                    raise serializers.ValidationError(
                        ("There aren't enough cash in the account to buy such a quantity of dtocks"), code='invalid')

        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist('No Inventory seller matches the given query')


class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class InventoryDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = Inventory
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class TradeSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField()
    buyer = serializers.StringRelatedField()
    class Meta:
        model = Trade
        fields = ('description', 'seller', 'buyer')


class TradeDetailSerializer(serializers.ModelSerializer):
    # seller = serializers.StringRelatedField()
    # buyer = serializers.StringRelatedField()
    # buyer_offer = serializers.StringRelatedField()
    # seller_offer = serializers.StringRelatedField()


    class Meta:
        model = Trade
        fields = '__all__'
