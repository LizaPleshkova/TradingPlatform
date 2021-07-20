from decimal import Decimal
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile, OfferCnoice


class BaseService:

    def get_validate_data(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer, serializer.validated_data


class OfferService(BaseService):

    def get_validate_data(self, request):
        request.data['user'] = request.user.id
        return super(OfferService, self).get_validate_data(request)


class TradeService:
    # Прицип работы: Пользователь может создавать Offer на покупку или продажу указывая количество и стоимость.
    # Celery запускает скрипт каждую минуту который ищет подходящие Offers на покупку и продажу.
    # Требования для сделки:
    #           цена покупки <= числа продажи,
    #           количество покупки <= количеству продажи
    # (мы можем купить наши Items у нескольких продавцов), скрипт должен находить выгодные предложения.

    @staticmethod
    def requiremenets_for_transaction(buyer_user: User):
        '''
        должно ли что-то получать на вход?нет
        здесь будет сама логика для поиска заявок:
            1цена покупки <= цена продажи,
            2количество покупки <= количеству продажи

        return объекты ( Offers), кототрые удовлетворяют условиям
        '''

        # получаем все офферы пользователя для покупки
        user_offers_buyer = Offer.objects.filter(user=buyer_user, type_transaction=OfferCnoice.BUY)

        # получаем все офферы для продажи
        offers_seller = Offer.objects.filter(type_transaction=OfferCnoice.SELL)

        # цикл для проверки самх условий

        for user_offer in user_offers_buyer:
            for offer_seller in offers_seller:
                # \sale_price = Item.objects.get(item_price=user_offer.item)
                # sale_price_obj = Price.objects.get(item_price=user_offer.item_offer.item_price)
                # sale_price = sale_price_obj.price # get price for sale

                # условие (0) : user_offer.item == offer_seller.item # зафвки на одну и ту же items

                # условие (1) : user_offer.price <= sale_price_obj.price

                # условие (2) : user_offer.quantity <= offer_seller.quantity
                # ?можем купить наши Items у нескольких продавцов?

                # если ок - добавлять в ?список(во что сохранять)
                pass

    @staticmethod
    def updating_user_score(user_id, user_offer: Offer, buyer_offer=None):
        try:
            # user_profile = get_object_or_404(UserProfile, user_id=user_id)
            user_profile = UserProfile.objects.get(user_id=user_id)
            if user_offer.type_transaction == OfferCnoice.BUY.name:
                user_profile.score = user_profile.score - user_offer.price * user_offer.quantity
            elif user_offer.type_transaction == OfferCnoice.SELL.name:
                user_profile.score = user_profile.score + buyer_offer.price * buyer_offer.quantity
            user_profile.save(update_fields=["score"])
        except UserProfile.DoesNotExist:
            return "No UserProfile  matches the given query."
            # raise ObjectDoesNotExist("No UserProfile  matches the given query.")

    @staticmethod
    def updating_inventory_buyer(user: User, user_offer: Offer):
        inventory_buyer, created = Inventory.objects.get_or_create(user=user, item=user_offer.item)
        if created:
            inventory_buyer.quantity = user_offer.quantity
        else:
            inventory_buyer.quantity += user_offer.quantity
        inventory_buyer.save(update_fields=["quantity"])
        return inventory_buyer

    @staticmethod
    def updating_inventory_seller(user: User, user_offer: Offer, buyer_offer: Offer):
        try:
            inventory_seller = Inventory.objects.get(user=user, item=user_offer.item)
            inventory_seller.quantity -= buyer_offer.quantity
            inventory_seller.save(update_fields=["quantity"])
            return inventory_seller
        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist("No Inventory seller matches the given query.")

    @staticmethod
    def updating_price_item(buyer_offer: Offer):
        price_item = buyer_offer.item.item_price.get()
        price_item.price += Decimal(buyer_offer.price) * Decimal(0.01)
        price_item.save(update_fields=["price"])
