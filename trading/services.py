from decimal import Decimal
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

import TradingPlatform
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

    @staticmethod
    def requiremenets_for_transaction(buyer_user):
        '''
        здесь будет сама логика для поиска заявок:
            1цена покупки <= цена продажи,
            2количество покупки <= количеству продажи
        return ( Offers), кототрые удовлетворяют условиям
        '''

        print('from sevices')
        # получаем все офферы пользователя для покупки
        user_offers_buyer = Offer.objects.filter(user=buyer_user, type_transaction=OfferCnoice.BUY.name)
        print('user_offers_buyer', user_offers_buyer)

        # получаем все офферы для продажи
        offers_seller = Offer.objects.filter(type_transaction=OfferCnoice.SELL.name)
        print(' offers_seller', offers_seller)
        # цикл для проверки самх условий
        out_offers_list = []
        for user_offer in user_offers_buyer:
            print(' user_offer', user_offer)
            for offer_seller in offers_seller:
                print('\t', 'offer_seller', offer_seller)

                # условие (0) : user_offer.item == offer_seller.item
                if user_offer.item == offer_seller.item:  # зафвки на одну и ту же items
                    print('\t\t', '(0) user_offer.item == offer_seller.item', user_offer.item, offer_seller.item)

                    sale_price = TradeService._get_sale_price_item(user_offer)  # get price for sale
                    print('\t\t', 'sale_price item seller)', sale_price)

                    # условие (1) : user_offer.price <= sale_price_obj.price
                    if user_offer.price <= sale_price:  # цена покупки <= цена продажи
                        print('\t\t', '(1) user_offer.price ', user_offer.price, ' sale_price ', sale_price)

                        # условие (2) : user_offer.quantity <= offer_seller.quantity
                        if user_offer.quantity <= offer_seller.quantity:  # количество покупки <= количеству продажи
                            print('\t\t', '(3)', user_offer.quantity,
                                  offer_seller.quantity)
                            print('\t\t', 'OK ', end='\n\n')
                            out_offers_list.append(offer_seller)

        return out_offers_list

    @staticmethod
    def _get_sale_price_item(user_offer: Offer):
        ''' get price for sale '''
        price_item = user_offer.item.item_price.get()
        print('\t\t', 'price_item', price_item)
        sale_price = price_item.price
        return sale_price

    @staticmethod
    def updating_user_score(user_id, user_offer: Offer, buyer_offer=None):
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            if user_offer.type_transaction == OfferCnoice.BUY.name:
                user_profile.score = user_profile.score - user_offer.price * user_offer.quantity
            elif user_offer.type_transaction == OfferCnoice.SELL.name:
                user_profile.score = user_profile.score + buyer_offer.price * buyer_offer.quantity
            user_profile.save(update_fields=["score"])
        except UserProfile.DoesNotExist:
            return "No UserProfile  matches the given query."

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

#
#
# if '__main__':
#
#     import psycopg2
#
#     con = psycopg2.connect(
#         database="trading_db",
#         user="admin",
#         password="admin",
#         host="127.0.0.1",
#         port="5432"
#     )
#
#     print("Database opened successfully")
#     cur = con.cursor()
#     cur.execute("SELECT * from auth_user where id=7")
#
#     rows = cur.fetchall()
#     for row in rows:
#         print("ADMISSION =", row[0])
#         print("NAME =", row[1])
#         print("AGE =", row[2])
#         print("COURSE =", row[3])
#         print("DEPARTMENT =", row[4], "\n")
#
#     print("Operation done successfully")
#     con.close()
#     script, first, second, third = argv
#
#     # print("Этот скрипт называется: ", script)
#     # print("Значение первой переменной: ", first)
#
#     user1 = User.objects.get(id=1)
#     TradeService.requiremenets_for_transaction(user1)
