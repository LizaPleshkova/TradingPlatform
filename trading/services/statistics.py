from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Count, F, Q, Sum
from trading.enums import OfferCnoice
from trading.models import Currency, Item, Trade
from trading.serializers import (
    PopularObjectSerializer, ItemSerializer
)


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
