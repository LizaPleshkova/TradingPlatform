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

    @staticmethod
    def requiremenets_for_transaction():
        '''
        здесь будет сама логика для поиска заявок:
            1цена покупки <= цена продажи,
            2количество покупки <= количеству продажи
        если все ок = сделка
        '''
        dict_trade = list()
        print('from sevices')
        buyer_offers = Offer.objects.filter(type_transaction=OfferCnoice.BUY.name)  # все офферы для покупки
        seller_offers = Offer.objects.filter(type_transaction=OfferCnoice.SELL.name)  # все офферы для продажи
        i = 0
        for buyer_offer in buyer_offers:
            print('buyer_offer', buyer_offer)
            for seller_offer in seller_offers:
                print('\t', 'seller_offer', seller_offer)

                # условие (0) : user_offer.item == offer_seller.item
                if buyer_offer.item == seller_offer.item:  # зафвки на одну и ту же items
                    print('\t\t', '(0) user_offer.item == seller_offer.item', buyer_offer.item,
                          seller_offer.item)

                    # условие (1) : user_offer.price <= sale_price_obj.price
                    if buyer_offer.price <= seller_offer.price:  # цена покупки <= цена продажи
                        print('\t\t', '(1) buyer_offer.price ', buyer_offer.price, ' seller_offer.price ',
                              seller_offer.price)

                        # условие (2) : user_offer.quantity <= offer_seller.quantity
                        if buyer_offer.quantity <= seller_offer.quantity:  # количество покупки <= количеству продажи
                            # купили столько акций, сколько было необходимо ( указано в заявке)
                            print('\t\t', '(3)', buyer_offer.quantity, seller_offer.quantity)
                            print('\t\t', 'OK ', end='\n\n')

                            seller_offer.quantity = seller_offer.quantity - buyer_offer.quantity
                            seller_offer.save(update_fields=["quantity"])

                            buyer_offer.is_active = False
                            buyer_offer.save(update_fields=["is_active"])

                            i += 1
                            s = OfferListSerializer(seller_offer)
                            b = OfferListSerializer(buyer_offer)
                            dict_trade.append(s.data)
                            dict_trade.append(b.data)

                        elif buyer_offer.quantity > seller_offer.quantity:
                            # будеv покупать по нескольких заявкам на продажу
                            # нужно изменить оффер на покупку (buyer_offer.quantity = buyer_offer.quantity - seller_offer.quantity
                            # изменить оффер на продажуу buyer_offer.is_zctive = False

                            buyer_offer.quantity = buyer_offer.quantity - seller_offer.quantity
                            buyer_offer.save(update_fields=["quantity"])

                            seller_offer.is_active = False
                            seller_offer.save(update_fields=["is_active"])

                            s = OfferListSerializer(seller_offer)
                            b = OfferListSerializer(buyer_offer)
                            dict_trade.append(s.data)
                            dict_trade.append(b.data)

        return dict_trade
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
