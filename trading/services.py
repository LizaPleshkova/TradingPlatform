from decimal import Decimal

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404

from .enums import OfferCnoice
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, Ip, UserProfile
from .serializers import (
    OfferListSerializer, ItemSerializer, WatchListSerializer, CurrencySerializer, PriceSerializer,
    OfferDetailSerializer, ItemDetailSerializer, TradeDetailSerializer, InventoryDetailSerializer, InventorySerializer,
    PriceDetailSerializer, CurrencyDetailSerializer, PopularItemSerializer, OfferRetrieveSerializer,
    PopularOfferSerializer, PopularObjectSerializer, PopularCurrencySerializer
)


class StatisticService:
    @staticmethod
    def get_popular_objects():
        # popular_offer = Offer.objects.annotate(hits=Count('counts_views')).order_by('-hits').first()
        popular_item = Item.objects.annotate(count_offers=Count('item_offer')).order_by('-count_offers').first()
        popular_currency = Currency.objects.annotate(counts_currency=Count('currency_item')).order_by(
            '-counts_currency').first()

        popular_objects = {
            'popular_item': popular_item,
            'popular_currency': popular_currency,
        }

        # work
        # pidict = model_to_dict(popular_item)
        # pidict['count_offers']= popular_item.count_offers
        # popular_objects = {
        #     # 'popular_offer': model_to_dict(popular_offer),
        #     'popular_item':pidict,
        #     'popular_currency': model_to_dict(popular_currency),
        # }

        ser_cur = PopularCurrencySerializer(popular_currency)
        ser = PopularObjectSerializer(popular_objects)

        return ser.data

    @staticmethod
    def get_best_items():
        ''' get best-selling/best-buying items'''

        return

    @staticmethod
    def smth():
        ''' на сколько сегодня было совершено сделок'''

    @staticmethod
    def smth():
        ''' какие акции купили продали сегодня'''


def _updating_offer_quantity(offer1, offer2):
    ''' offer1 > offer2 '''
    offer1.quantity = offer1.quantity - offer2.quantity
    offer1.save(update_fields=["quantity"])
    return offer1


def _updating_offer_is_active(offer):
    offer.is_active = False
    offer.save(update_fields=["is_active"])
    return offer


class ProfitableTransactionsServices:

    @staticmethod
    def requirements_for_transaction():
        buyer_offers = Offer.objects.filter(type_transaction=OfferCnoice.BUY.value, is_active=True).select_related(
            'user__user_profile')  # все офферы для покупки
        seller_offers = Offer.objects.filter(type_transaction=OfferCnoice.SELL.value, is_active=True).select_related(
            'user__user_profile')  # все офферы для продажи

        for buyer_offer in buyer_offers:
            for seller_offer in seller_offers:
                ProfitableTransactionsServices.checking_offers(buyer_offer, seller_offer)

    @staticmethod
    def checking_offers(buyer_offer: Offer, seller_offer: Offer):
        if buyer_offer.item == seller_offer.item:  # зафвки на одну и ту же items

            if buyer_offer.price <= seller_offer.price:
                ProfitableTransactionsServices.checking_offers_quantity(buyer_offer, seller_offer)

    @staticmethod
    def checking_offers_quantity(buyer_offer: Offer, seller_offer: Offer):
        if buyer_offer.quantity <= seller_offer.quantity:
            # купили столько акций, сколько было необходимо ( указано в заявке)

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)

            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks "
            )

            if buyer_offer.quantity - seller_offer.quantity == 0:
                _updating_offer_is_active(seller_offer)
            _updating_offer_quantity(seller_offer, buyer_offer)
            _updating_offer_is_active(buyer_offer)

        elif buyer_offer.quantity > seller_offer.quantity:
            # покупка акций по нескольким офферс

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)

            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks "
            )

            _updating_offer_quantity(buyer_offer, seller_offer)
            _updating_offer_is_active(seller_offer)
        return trade


class TradeService:

    @staticmethod
    def updating_inventory_buyer(seller_offer: Offer, buyer_offer: Offer):
        inventory_buyer, created = Inventory.objects.get_or_create(user=buyer_offer.user, item=buyer_offer.item)
        if buyer_offer.quantity > seller_offer.quantity:
            if created:
                inventory_buyer.quantity = seller_offer.quantity
            else:
                inventory_buyer.quantity += seller_offer.quantity
        elif buyer_offer.quantity <= seller_offer.quantity:
            if created:
                inventory_buyer.quantity = buyer_offer.quantity
            else:
                inventory_buyer.quantity += buyer_offer.quantity
        inventory_buyer.save(update_fields=["quantity"])

    @staticmethod
    def updating_inventory_seller(seller_offer: Offer, buyer_offer: Offer):
        '''updating_inventory_seller'''
        # inventory_seller = Inventory.objects.get(user=seller_offer.user, item=seller_offer.item)
        inventory_seller = get_object_or_404(Inventory, user=seller_offer.user, item=seller_offer.item)
        if buyer_offer.quantity > seller_offer.quantity:
            inventory_seller.quantity -= seller_offer.quantity
        elif buyer_offer.quantity <= seller_offer.quantity:
            inventory_seller.quantity -= buyer_offer.quantity
        inventory_seller.save(update_fields=["quantity"])
        return inventory_seller

    @staticmethod
    def updating_users_score(seller_offer: Offer, buyer_offer: Offer):
        try:
            seller_profile = seller_offer.user.user_profile
            buyer_profile = buyer_offer.user.user_profile

            if buyer_offer.quantity > seller_offer.quantity:
                buyer_profile.score = buyer_profile.score - seller_offer.quantity * buyer_offer.price
                seller_profile.score = seller_profile.score + seller_offer.quantity * buyer_offer.price
            elif buyer_offer.quantity <= seller_offer.quantity:
                buyer_profile.score = buyer_profile.score - buyer_offer.quantity * buyer_offer.price
                seller_profile.score = seller_profile.score + buyer_offer.quantity * buyer_offer.price
            buyer_profile.save(update_fields=["score"])
            seller_profile.save(update_fields=["score"])
            return buyer_profile, seller_profile
        except UserProfile.DoesNotExist:
            return "No UserProfile  matches the given query."

    @staticmethod
    def updating_price_item(buyer_offer: Offer):
        try:
            price_item = buyer_offer.item.item_price.get()
            price_item.price += Decimal(buyer_offer.price) * Decimal(0.05)
            price_item.save(update_fields=["price"])
        except Price.DoesNotExist:
            raise ObjectDoesNotExist('No Price matches the given query')


# Метод для получения айпи
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')  # В REMOTE_ADDR значение айпи пользователя
    return ip
#
