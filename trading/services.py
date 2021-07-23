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
        # # получаем все офферы пользователя для покупки\продажи
        # user_offers_buyer = Offer.objects.filter(user=buyer_user)
        # print('user_offers_buyer', user_offers_buyer)
        #
        # # получаем все офферы для продажи\покупки крое офферов пользователя
        # offers_seller = Offer.objects.exclude(user=buyer_user)
        # print(' offers_seller', offers_seller)
        #
        # # цикл для проверки самх условий
        # out_offers_list = []
        # for user_offer in user_offers_buyer:
        #     print(' user_offer', user_offer)
        #     for offer_seller in offers_seller:
        #         print('\t', 'offer_seller', offer_seller)
        #
        #         # условие (0) : user_offer.item == offer_seller.item
        #         if user_offer.item == offer_seller.item and user_offer.type_transaction != offer_seller.type_transaction:  # зафвки на одну и ту же items
        #             print('\t\t', '(0) user_offer.item == offer_seller.item', user_offer.item, offer_seller.item)
        #
        #             sale_price = TradeService._get_sale_price_item(user_offer)  # get price for sale
        #             print('\t\t', 'sale_price item seller)', sale_price)
        #
        #             # условие (1) : user_offer.price <= sale_price_obj.price
        #             if user_offer.price <= sale_price:  # цена покупки <= цена продажи
        #                 print('\t\t', '(1) user_offer.price ', user_offer.price, ' sale_price ', sale_price)
        #
        #                 # условие (2) : user_offer.quantity <= offer_seller.quantity
        #                 if user_offer.quantity <= offer_seller.quantity:  # количество покупки <= количеству продажи
        #                     print('\t\t', '(3)', user_offer.quantity,
        #                           offer_seller.quantity)
        #                     print('\t\t', 'OK ', end='\n\n')
        #                     out_offers_list.append(offer_seller)


def _updating_offer_quantity(offer1, offer2):
    ''' offer1 > offer2 '''
    offer1.quantity = offer1.quantity - offer2.quantity
    offer1.save(update_fields=["quantity"])


def _updating_offer_is_active(offer):
    offer.is_active = False
    offer.save(update_fields=["is_active"])


class ProfitableTransactionsServices:

    @staticmethod
    def requiremenets_for_transaction():
        '''
       сама логика для поиска заявок:
            0items равны в офферах на покупку\продажу + офферы is_active=True
            1цена покупки <= цена продажи,
            2количество покупки <= количеству продажи
            3количество покупки > количеству продажи
        если все ок = сделка
        '''
        # dict_trade = list()

        buyer_offers = Offer.objects.filter(type_transaction=OfferCnoice.BUY.name)  # все офферы для покупки
        seller_offers = Offer.objects.filter(type_transaction=OfferCnoice.SELL.name)  # все офферы для продажи
        # print('buyer_offers', buyer_offers)
        # print('seller_offer/', seller_offers)

        for buyer_offer in buyer_offers:
            # print('buyer_offer', buyer_offer)
            for seller_offer in seller_offers:
                # print('\t', 'seller_offer', seller_offer)

                # dict_trade = ProfitableTransactionsServices.checking_offers(buyer_offer, seller_offer)
                ProfitableTransactionsServices.checking_offers(buyer_offer, seller_offer)

        # return dict_trade

    @staticmethod
    def checking_offers(buyer_offer, seller_offer):
        # dict_trade = list()
        # условие (0) : user_offer.item == offer_seller.item
        if buyer_offer.item == seller_offer.item and seller_offer.is_active == True and buyer_offer.is_active == True:  # зафвки на одну и ту же items
            # print('\t\t', '(0) user_offer.item == seller_offer.item', buyer_offer.item,
            #       seller_offer.item)

            # условие (1) : user_offer.price <= sale_price_obj.price
            if buyer_offer.price <= seller_offer.price:  # цена покупки <= цена продажи
                # print('\t\t', '(1) buyer_offer.price ', buyer_offer.price, ' seller_offer.price ',
                #       seller_offer.price)

                # условие (2) : user_offer.quantity <= offer_seller.quantity
                # dict_trade = ProfitableTransactionsServices.checking_offers_quantity(buyer_offer, seller_offer)
                ProfitableTransactionsServices.checking_offers_quantity(buyer_offer, seller_offer)

        # return dict_trade

    @staticmethod
    def checking_offers_quantity(buyer_offer, seller_offer):
        # dict_trade = list()
        if buyer_offer.quantity <= seller_offer.quantity:  # количество покупки <= количеству продажи
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
            print('\t\t', 'TRADE ', trade, end='\n\n')

            _updating_offer_quantity(seller_offer, buyer_offer)
            _updating_offer_is_active(buyer_offer)
            # dict_trade.append(trade)

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
            print('\t\t', 'TRADE ', trade, end='\n\n')

            _updating_offer_quantity(buyer_offer, seller_offer)
            _updating_offer_is_active(seller_offer)

            # dict_trade.append(trade)

        # return dict_trade


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
        # print('inventory_buyer.quantity ', inventory_buyer.quantity)
        inventory_buyer.save(update_fields=["quantity"])

    @staticmethod
    def trade(seller_offer, buyer_offer):

        TradeService.updating_price_item(buyer_offer)

    @staticmethod
    def _get_sale_price_item(user_offer: Offer):
        ''' get price for sale '''
        price_item = user_offer.item.item_price.get()
        print('\t\t', 'price_item', price_item)
        sale_price = price_item.price
        return sale_price

    @staticmethod
    def updating_users_score(seller_offer: Offer, buyer_offer: Offer):
        try:
            seller_profile = UserProfile.objects.get(user_id=seller_offer.user.id)
            buyer_profile = UserProfile.objects.get(user_id=buyer_offer.user.id)

            if buyer_offer.quantity > seller_offer.quantity:
                # если пользователь покупает = деньги списываются со счета
                buyer_profile.score = buyer_profile.score - seller_offer.quantity * buyer_offer.price

                # если пользователь продает = деньги добавляются со счета
                seller_profile.score = seller_profile.score + seller_offer.quantity * buyer_offer.price

            elif buyer_offer.quantity <= seller_offer.quantity:
                # если пользователь покупает = деньги списываются со счета
                buyer_profile.score = buyer_profile.score - buyer_offer.quantity * buyer_offer.price
                # если пользователь продает = деньги добавляются со счета
                seller_profile.score = seller_profile.score + buyer_offer.quantity * buyer_offer.price
            # print(' buyer_profile.score ', buyer_profile.score, '\n', 'seller_profile.score', seller_profile.score)
            buyer_profile.save(update_fields=["score"])
            seller_profile.save(update_fields=["score"])
        except UserProfile.DoesNotExist:
            return "No UserProfile  matches the given query."

    @staticmethod
    def updating_inventory_seller(seller_offer: Offer, buyer_offer: Offer):
        '''updating_inventory_seller'''
        try:
            inventory_seller = Inventory.objects.get(user=seller_offer.user, item=seller_offer.item)
            if buyer_offer.quantity > seller_offer.quantity:
                inventory_seller.quantity -= seller_offer.quantity
            else:
                inventory_seller.quantity -= buyer_offer.quantity
            # print('inventory_seller.quantity ', inventory_seller.quantity)
            inventory_seller.save(update_fields=["quantity"])
            return inventory_seller
        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist("No Inventory seller matches the given query.")

    @staticmethod
    def updating_price_item(buyer_offer: Offer):
        price_item = buyer_offer.item.item_price.get()
        price_item.price += Decimal(buyer_offer.price) * Decimal(0.01)
        price_item.save(update_fields=["price"])
