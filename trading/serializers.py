import json
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
        # exclude = ('name',)
        fields = '__all__'


class CurrencyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class OfferPriceUserSerializer(serializers.ModelSerializer):
    sum_offers = serializers.IntegerField()

    class Meta:
        model = Offer
        fields = ('type_transaction', 'item', 'user', 'sum_offers')


class PopularItemSerializer(serializers.ModelSerializer):
    count_offers = serializers.IntegerField(required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        currency = representation['currency']
        for curr in currency:
            if curr == 'code':
                representation['currency'] = currency[curr]
        return json.dumps(representation)

    class Meta:
        model = Item
        fields = '__all__'
        depth = 1


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # fields = ('code', 'name',)
        fields = '__all__'


class OfferListSerializer(serializers.Serializer):
    class Meta:
        model = Offer
        exclude = ('price', 'quantity', 'is_active', 'counts_views')


class OfferRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        # fields = '__all__'
        exclude = ('price',)

    def to_representation(self, data):
        representation = super().to_representation(data)

        id = representation['id']
        ob1 = Offer.objects.get(id=id)
        representation['counts_views'] = ob1.counts_views.count()
        return representation


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

    def validate(self, data):
        """ checking quantity seller's stocks """
        try:
            if data.get('type_transaction') == OfferCnoice.SELL.value:
                inventory_seller = Inventory.objects.get(user=data.get('user'), item=data.get('item'))
                if inventory_seller.quantity <= data.get('quantity'):
                    raise serializers.ValidationError('You want to sell more stocks than you have', code='invalid')
            if data.get('type_transaction') == OfferCnoice.BUY.value:
                buyer_profile = data.get('user').user_profile
                if buyer_profile.score <= (data.get('quantity') * data.get('price')):
                    raise serializers.ValidationError(
                        "There aren't enough cash in the account to buy such a quantity of dtocks", code='invalid'
                    )
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

    def to_internal_value(self, data):
        try:
            item_data = data['user']
            for i in item_data:
                user = User.objects.get(username=item_data[i])
            data['user'] = user.id
            return super().to_internal_value(data)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User does not exist.'
            )


class InventoryDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = Inventory
        fields = '__all__'
    #
    # def to_representation(self, obj):
    #     representation = super().to_representation(obj)
    #
    #     item_representation = representation.pop('item')
    #     for key in item_representation:
    #         representation[f'item {key}'] = item_representation[key]
    #     return representation


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


class PopularItemSerializer(ItemSerializer):
    count_offers = serializers.IntegerField()


class PopularOfferSerializer(OfferListSerializer):
    hits = serializers.IntegerField()


class PopularCurrencySerializer(CurrencySerializer):
    counts_currency = serializers.IntegerField()


class PopularObjectSerializer(serializers.Serializer):
    popular_offer = PopularOfferSerializer()
    popular_currency = PopularCurrencySerializer()
