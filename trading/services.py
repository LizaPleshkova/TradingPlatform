from decimal import Decimal

from django.core.serializers import get_serializer
from django.http import Http404
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, InventorySerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile, OfferCnoice

class BaseService:

    @staticmethod
    def get_validate_data(request):
        serializer = OfferListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer, serializer.validated_data

    @staticmethod
    def get_validate_data_trade(request):
        serializer = TradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer, serializer.validated_data


class OfferService(BaseService):

    @staticmethod
    def get_validate_data(request):
        request.data['user'] = request.user.id
        return super(OfferService, OfferService).get_validate_data(request)
        #        {
        #     'type_transaction': serializer.validated_data.get('type_transaction'),
        #     'item': serializer.validated_data.get('type_transaction'),
        #     'user': self.request.user.id,
        #     'price': serializer.validated_data.get('price'),
        #     'quantity': serializer.validated_data.get('quantity'),
        # }

    @staticmethod
    def checking_quantity_stocks_seller(data):
        # if data.get('type_transaction') == OfferCnoice.SELL:
        if data.get('type_transaction') == 'SELL':
            try:
                inventory_seller = Inventory.objects.get(user=data.get('user'),
                                                         item=data.get('item'))
                if inventory_seller.quantity < data.get('quantity'):
                    # return Response({'You want to sell more stocks than you have'}, status=status.HTTP_400_BAD_REQUEST)
                    raise ValueError('You want to sell more stocks than you have')
            except Inventory.DoesNotExist:
                # return Response({"No Inventory seller matches the given query."}, status=status.HTTP_400_BAD_REQUEST)
                raise ObjectDoesNotExist('No Inventory seller matches the given query')


class TradeService:

    @staticmethod
    def updating_user_score(user_id, user_offer, buyer_offer=None):
        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        if user_offer.type_transaction == "BUY":
            user_profile.score = user_profile.score - user_offer.price * user_offer.quantity
        elif user_offer.type_transaction == "SELL":
            user_profile.score = user_profile.score + buyer_offer.price * buyer_offer.quantity
        user_profile.save(update_fields=["score"])
        return user_profile

    @staticmethod
    def updating_inventory_buyer(user, user_offer):
        inventory_buyer, created = Inventory.objects.get_or_create(user=user, item=user_offer.item)
        if created:
            inventory_buyer.quantity = user_offer.quantity
        else:
            inventory_buyer.quantity += user_offer.quantity
        inventory_buyer.save(update_fields=["quantity"])
        return inventory_buyer

    @staticmethod
    def updating_inventory_seller(user, user_offer, buyer_offer):
        try:
            # inventory_seller = get_object_or_404(Inventory, user=user, item=user_offer.item)
            inventory_seller = Inventory.objects.get(user=user, item=user_offer.item)
            inventory_seller.quantity -= buyer_offer.quantity
            inventory_seller.save(update_fields=["quantity"])
            return inventory_seller

        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist("No Inventory seller matches the given query.")

    @staticmethod
    def updating_price_item(buyer_offer):
        price_item = buyer_offer.item.item_price.get()
        price_item.price += Decimal(buyer_offer.price) * Decimal(0.01)
        price_item.save(update_fields=["price"])