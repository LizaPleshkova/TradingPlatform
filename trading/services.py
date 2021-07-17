from django.http import Http404
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import status

from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, InventorySerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile


class TradeService():

    def updating_user_score(self, user_id, user_offer, buyer_offer=None):
        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        if user_offer.type_transaction == "BUY":
            user_profile.score = user_profile.score - user_offer.price * user_offer.quantity
        elif user_offer.type_transaction == "SELL":
            user_profile.score = user_profile.score + buyer_offer.price * buyer_offer.quantity
        user_profile.save()
        return user_profile

    def updating_inventory_buyer(self, user, user_offer):
        inventory_buyer, created = Inventory.objects.get_or_create(user=user, item=user_offer.item)
        if created:
            obj = Inventory.objects.get(user=user, item=user_offer.item)
            obj.quantity = user_offer.quantity
            obj.save()
        else:
            inventory_buyer.quantity += user_offer.quantity
            inventory_buyer.save()
        return inventory_buyer

    def updating_inventory_seller(self, user, user_offer, buyer_offer):
        # try:
        inventory_seller = get_object_or_404(Inventory, user=user, item=user_offer.item)
        # inventory_seller = Inventory.objects.get(user=user, item=user_offer.item)
        inventory_seller.quantity -= buyer_offer.quantity
        inventory_seller.save()
        # except Inventory.DoesNotExist:
        #     raise DoesNotExist
        #     # ({"No Inventory seller matches the given query."}, status=status.HTTP_400_BAD_REQUEST)
        return inventory_seller
