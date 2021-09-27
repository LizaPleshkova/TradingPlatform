from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404

from .enums import OfferCnoice
from .models import Currency, Item, Price, Offer, Trade, Inventory, UserProfile
from .serializers import (
    PopularObjectSerializer, AttachPaymentMethodToCustomerSerializer,
    CreatePaymentMethodCardSerializer, ConfirmPaymentSerializer, CreatePaymentIntentSerializer, ItemSerializer,
    CurrencySerializer, CurrencyFromExcel
)
import stripe
from pathlib import Path
import pandas as pd


def _sheets_to_dict(excel_file):
    data_records = {}
    for sheet in excel_file.sheet_names:
        d = excel_file.parse(sheet).to_dict('records')
        data_records[sheet] = d
    return data_records


def _validate_excel_data_columns(data_dict_sheets):
    for sheet in data_dict_sheets:
        if 'id' in data_dict_sheets[sheet]:
            data_dict_sheets[sheet] = data_dict_sheets[sheet].drop(columns='id')
        if 'code' in data_dict_sheets[sheet] or 'name' in data_dict_sheets[sheet]:
            data_dict_sheets[sheet] = data_dict_sheets[sheet].to_dict('records')
            _save_excel_data(data_dict_sheets[sheet])
    return data_dict_sheets


def _save_excel_data(excel_data_dict):
    ser = CurrencySerializer(data=excel_data_dict, many=True)
    ser.is_valid(raise_exception=True)
    cur_list = [Currency(code=i['code'], name=i['name']) for i in ser.validated_data]
    Currency.objects.bulk_create(cur_list)
    print('cur_list',cur_list)
    return cur_list


class ImportExcelService:
    '''
    разбей все по методам. Порефактори. И сделай возможность имплорта как из эксель так и с помощью csv
    '''
    @staticmethod
    def import_excel_sheets(file_name):
        '''
        +
        import data from all sheets of the excel-file
        '''
        file_path = Path(file_name)
        if file_path.suffix == '.xlsx' or file_path.suffix == '.xls':
            xl = pd.ExcelFile(file_name)
            return _sheets_to_dict(xl)
        else:
            raise ValueError('needs the format file .xlsx or .xls')

    @staticmethod
    def import_currency_to_excel(file_name):

        file_path = Path(file_name)
        if file_path.suffix == '.xlsx' or file_path.suffix == '.xls':
            # get dict with all sheets from excel file with values (DataFrame)
            xl = pd.ExcelFile(file_name)
            sheets = xl.sheet_names
            data_dict_sheets = {}
            for sheet in sheets:
                d = xl.parse(sheet)
                data_dict_sheets[sheet] = d

            data_dict_sheets = _validate_excel_data_columns(data_dict_sheets)
            return data_dict_sheets
            #
            # for sheet in data_dict_sheets:
            #     if 'id' in data_dict_sheets[sheet]:
            #         data_dict_sheets[sheet] = data_dict_sheets[sheet].drop(columns='id')
            #     if 'code' in data_dict_sheets[sheet] or 'name' in data_dict_sheets[sheet]:
            #         # dataframe to dict
            #         data_dict_sheets[sheet] = data_dict_sheets[sheet].to_dict('records')
            #         ser = CurrencySerializer(data=data_dict_sheets[sheet], many=True)
            #         ser.is_valid(raise_exception=True)
            #         cur_list = [Currency(code=i['code'], name=i['name']) for i in ser.validated_data]
            #         Currency.objects.bulk_create(cur_list)
            # return data_dict_sheets

        else:
            raise ValueError('needs the format file .xlsx or .xls')


class ExportExcelService:

    @staticmethod
    def export_to_excel(file_name):
        try:
            # file_name = 'test.xlsx'
            file_path = Path(file_name)
            if file_path.suffix == '.xlsx':
                # количество листов!
                xslx = pd.read_excel(file_name, engine='openpyxl')
                sheet_dataframe = xslx.head()
                # проверка: есть ли столбец id
                if 'id' in sheet_dataframe:
                    sheet_dataframe = sheet_dataframe.drop(columns='id')
                excel_dict = sheet_dataframe.to_dict('records')
                for record in excel_dict:
                    if 'code' in record or 'name' in record:
                        ser = CurrencySerializer(data=excel_dict, many=True)
                        ser.is_valid(raise_exception=True)
                        cur_list = [Currency(code=i['code'], name=i['name']) for i in ser.validated_data]
                        Currency.objects.bulk_create(cur_list, ignore_conflicts=True)
                        return cur_list
                return excel_dict
            elif file_path.suffix == '.xls':
                df = pd.read_excel(file_name)
                print(df)
            else:
                # handle other file types
                pass
        except Exception:
            raise Exception


#
# if __name__ == "__main__":
#     df = ExportExcelService.export_to_excel()


class PaymentService:
    @staticmethod
    def create_payment_method_card(request):
        serializer = CreatePaymentMethodCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": serializer.validated_data['number'],
                "exp_month": serializer.validated_data['exp_month'],
                "exp_year": serializer.validated_data['exp_year'],
                "cvc": serializer.validated_data['cvc'],
            },
        )

        # for test
        # payment_method = stripe.PaymentMethod.retrieve(
        #     "pm_1JaLO3EYdpQ6mE0ASQzn2koT"  # for user3
        # )

        payment_method_attach = PaymentService.attach_payment_method_to_customer(request.user, payment_method['id'])
        return payment_method_attach

    @staticmethod
    def attach_payment_method_to_customer(user, payment_method_id):
        serializer = AttachPaymentMethodToCustomerSerializer(
            data={"payment_method_id": payment_method_id},
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)

        payment_method = stripe.PaymentMethod.attach(
            serializer.validated_data['payment_method_id'],
            customer=serializer.validated_data['customer']
        )
        # for test
        # payment_method = stripe.PaymentMethod.list(
        #     customer=serializer.validated_data['customer'],
        #     type="card"
        # )
        return payment_method

    @staticmethod
    def confirm_payment_intent(request):
        serializer = ConfirmPaymentSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        conf = stripe.PaymentIntent.confirm(
            serializer.validated_data['payment_intent_id'],
            payment_method=serializer.validated_data['payment_method_id'],
        )
        return conf

    @staticmethod
    def create_payment_intent(request):
        ser = CreatePaymentIntentSerializer(data=request.data, context={"user": request.user})
        ser.is_valid(raise_exception=True)

        test_payment_intent = stripe.PaymentIntent.create(
            amount=ser.validated_data['amount'],
            currency=ser.validated_data['currency'],
            payment_method_types=[ser.validated_data['payment_method_types']],
            customer=ser.validated_data['customer'],
            receipt_email=ser.validated_data['receipt_email']
        )

        # test_payment_intent = stripe.PaymentIntent.retrieve(
        #     "pi_3JaKRLEYdpQ6mE0A14ArQIp7"
        # )
        print(test_payment_intent['id'])

        return test_payment_intent


class StatisticService:

    @staticmethod
    def users_statistic(user_id):
        user_trade_today_count = StatisticService.user_trade_today_count(user_id)
        items_today = StatisticService.items_today(user_id)
        sum_trades = StatisticService.sum_user_trade_today(user_id)
        statistic_user = {
            'user_trade_today_count': user_trade_today_count,
            'items_today': items_today,
            'user_sum': sum_trades
        }

        return statistic_user

    @staticmethod
    def sum_user_trade_today(user_id):
        '''
        trade for user's buying
        '''

        user_trades_sum_buy = User.objects.filter(
            id=user_id
        ).aggregate(
            buy_trade_sum=Sum(F('buyer_trade__price') * F('buyer_trade__quantity'), dictinct=True),
        )

        user_trades_sum_sell = User.objects.filter(
            id=user_id
        ).aggregate(
            sell_trade_sum=Sum(F('seller_trade__price') * F('seller_trade__quantity'), dictinct=True)
        )

        # user_trades_sum = User.objects.filter(
        #     id=1
        # ).aggregate(
        #     buy_trade_sum=Sum(F('buyer_trade__price') * F('buyer_trade__quantity'), dictinct=True),
        #     sell_trade_sum=Sum(F('seller_trade__price') * F('seller_trade__quantity'), dictinct=True)
        # )

        return {
            'buy_trade_sum': user_trades_sum_buy,
            'sell_trade_sum': user_trades_sum_sell
        }

    @staticmethod
    def get_popular_objects():
        popular_item = Item.objects.annotate(count_offers=Count('item_offer')).order_by('-count_offers').first()
        popular_currency = Currency.objects.annotate(counts_currency=Count('currency_item')).order_by(
            '-counts_currency'
        ).first()

        popular_objects = {
            'popular_item': popular_item,
            'popular_currency': popular_currency,
        }
        serializer_objects = PopularObjectSerializer(popular_objects)
        return serializer_objects.data

    @staticmethod
    def user_trade_today_count(user_id):
        '''
        сколько сегодня было совершено сделок for buying/selling
        '''
        users_trades = User.objects.filter(
            id=user_id,
        ).annotate(
            buy_trades_count=Count(
                'user_offer__buy_trade',
                filter=Q(user_offer__type_transaction=OfferCnoice.BUY.value)
            ),
            sell_trades_count=Count(
                'user_offer__sell_trade',
                filter=Q(user_offer__type_transaction=OfferCnoice.SELL.value)
            )
        ).values('buy_trades_count', 'sell_trades_count').first()

        return {
            "buy_trades_count": users_trades['buy_trades_count'],
            "sell_trades_count": users_trades['sell_trades_count'],
        }

    @staticmethod
    def items_today_second(user):

        user_trades_buy = set()
        user_trades_sell = set()

        user_trades_today = Trade.objects.filter(
            Q(seller=user) | Q(buyer=user),
            trade_date__date=datetime.now().date()
        ).select_related('seller_offer__item', 'buyer_offer__item', 'seller', 'buyer')

        for trade in user_trades_today:
            if trade.buyer == user:
                user_trades_buy.add(trade.buyer_offer.item)
            elif trade.seller == user:
                user_trades_sell.add(trade.buyer_offer.item)

        return {
            'items_buy': ItemSerializer(user_trades_buy, many=True).data,
            'items_sell': ItemSerializer(user_trades_sell, many=True).data,
        }

    @staticmethod
    def items_today_third(user):

        user_trades_buy = set()
        user_trades_sell = set()

        user_trades_today = Trade.objects.filter(
            Q(seller=user) | Q(buyer=user),
            trade_date__date=datetime.now().date()
        ).select_related('seller_offer__item', 'buyer_offer__item', 'seller', 'buyer')

        for trade in user_trades_today:
            if trade.buyer == user:
                user_trades_buy.add(trade.buyer_offer.item)
            elif trade.seller == user:
                user_trades_sell.add(trade.buyer_offer.item)

        return {
            'items_buy': ItemSerializer(user_trades_buy, many=True).data,
            'items_sell': ItemSerializer(user_trades_sell, many=True).data,
        }

    @staticmethod
    def items_today(user_id):
        '''
        какие акции купили/продали сегодня
        '''

        # акции, которые купил user
        user_items_buy = Item.objects.filter(
            item_offer__buy_trade__trade_date__date=datetime.now().date(),
            item_offer__buy_trade__buyer=1
        ).values().distinct()

        # акции, которые продал user
        user_items_sell = Item.objects.filter(
            item_offer__sell_trade__trade_date__date=datetime.now().date(),
            item_offer__sell_trade__seller=user_id
        ).values().distinct()

        return {
            'items_buy': user_items_buy,
            'items_sell': user_items_sell,
        }


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
        print(buyer_offers, seller_offers, sep='\n')
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
            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks ",
                trade_date=datetime.now(),
                price=buyer_offer.price,
                quantity=buyer_offer.quantity,
            )

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)

            if buyer_offer.quantity - seller_offer.quantity == 0:
                _updating_offer_is_active(seller_offer)
            _updating_offer_quantity(seller_offer, buyer_offer)
            _updating_offer_is_active(buyer_offer)

        elif buyer_offer.quantity > seller_offer.quantity:
            # покупка акций по нескольким офферс
            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks ",
                trade_date=datetime.now(),
                price=buyer_offer.price,
                quantity=seller_offer.quantity,
            )

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)

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
