import sqlite3
from django.db import connection, reset_queries
import time
import functools
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, OfferCnoice, UserProfile
from django.db.models import Count, F, Q, Subquery, Exists, OuterRef, Case, When, Value, Sum, Max
import psycopg2


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        start_queries = len(connection.queries)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        end_queries = len(connection.queries)
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func


def connection_to_db():
    conn = psycopg2.connect(host='localhost', user='postgres', password='admin', dbname='trading_db')
    # Создаем курсор - это специальный объект который делает запросы и получает их результаты
    cursor = conn.cursor()
    print('oks')
    # Не забываем закрыть соединение с базой данных
    conn.close()


def task1():
    '''
    посчитать price всех офферов для определнног user

    users:
        3 user1
        1 admin

    хочу уточнить первое задание
    нужно посчитать price для всех офферов для определеьнного пользователя (это на какую сумму всего офферов?)
    тип sum(price*quantity)
    т.е. сумма оффера считается так (price*quantity)?
    '''

    offers = Offer.objects.values('user').annotate(sum_offers=Sum(F('price') * F('quantity')))
    offers = Offer.objects.annotate(sum_offers=Sum(F('price') * F('quantity')))

    offers = Offer.objects.filter(user=1).aggregate(sum_offers=Sum(F('price') * F('quantity')))


def task1():
    '''
    посчитать самый популярный item (большего всего офферов)

    users:
        3 user1
        1 admin
    '''

    item = Item.objects.annotate(count_offers=Count('item_offer')).order_by('-count_offers')[:1]

    item = Item.objects.annotate(count_offers=Count('item_offer'))
    item.filter(count_offers=3)
    item.aggregate(count_offers=Max('count_offers'))


@query_debugger
def ex1():
    ''' 0.000869 '''
    of1 = Offer.objects.filter(Q(is_active=True), Q(type_transaction=OfferCnoice.BUY.value))
    print('offers with Q()', of1)


@query_debugger
def ex2():
    '''   0.000279 '''
    off2 = Offer.objects.filter(type_transaction=OfferCnoice.BUY.value, is_active=True)
    print(off2)


def ex333():
    '''
    что быстрее = Count(F('item_offer'))
    '''
    item = Item.objects.annotate(count_offers=Count('item_offer'))
    itemF = Item.objects.annotate(count_offers=Count(F('item_offer')))


def ex3222():
    '''
    for this
    This time we used the function annotate. To produce a GROUP BY we use a combination of values and annotate:

    values('is_active'): what to group by
    annotate(total=Count('id')): what to aggregate
    акции определенной валюты ==
    about group by?


    Book.objects.group_by('title', 'author').annotate(
            shop_count=Count('shop'), price_avg=Avg('price')).order_by(
            'name', 'author').distinct()



    '''
    item = Item.objects.values('currency').annotate(count_offers=Count('id'))
    it = Item.objects.filter(currency__id=1).annotate(curr=Count('id'))


@query_debugger
def ex3():
    ''' 0.008013 '''
    item = Item.objects.annotate(count_offers=Count('item_offer', filter=(Q(item_offer__is_active=True))))
    for i in item:
        print(i.count_offers)


@query_debugger
def ex4():
    ''' .001007 '''
    # item = Item.objects.annotate(count_offers=Count('item_offer', filter=(Q(item_offer__is_active=True))))\
    #                     .aggregate(Count('count_offers', filter=Q(count_offers__gt=0)))-
    item = Item.objects.annotate(count_offers=Count('item_offer', filter=(Q(item_offer__is_active=True)))) \
        .filter(count_offers__gt=0) \
        .aggregate(Count('count_offers'))

    print(item)


@query_debugger
def ex5():
    '''
    SELECT "trading_item"."id",
       "trading_item"."code",
       "trading_item"."name",
       "trading_item"."currency_id",
       "trading_item"."description"
    FROM "trading_item"
    INNER JOIN "trading_offer"
    ON ("trading_item"."id" = "trading_offer"."item_id")
    WHERE "trading_offer"."id" IN (
        SELECT U0."id"
          FROM "trading_offer" U0
         WHERE U0."is_active"
       )
    '''
    offers = Offer.objects.filter(is_active=True)
    item = Item.objects.filter(item_offer__in=Subquery(offers.values('id')))  # 0.008986
    item = Item.objects.filter(item_offer__in=Subquery(offers.only('id')))  # 0.002002
    print(item)


def ex10():
    '''
    офферы у которых цена на продажу меньше, чем цена акций
    select *
    from trading_offer
    inner join trading_item on trading_item.id = trading_offer.item_id
    inner join trading_price on trading_price.item_id = trading_item.id
    where trading_price.price < trading_offer.price;
    '''

    offer = Offer.objects.filter(price__gt=F('item__item_price__price'))  # +
    offer.annotate(difference=F('item__item_price__price') - F('price'))

    # price = Price.objects.filter(item=OuterRef('id'))
    # offer.filter(price__lte=F('item__item_price__price'))
    price = Price.objects.filter(item=OuterRef('id'))
    items = Item.objects.filter(item_offer=OuterRef('id'))

    offer = Offer.objects.filter(item=Subquery(items.values('id')),
                                 item__item_price__price=Subquery(price.values('id')))
    offer = Offer.objects.filter(item=Subquery(items.values('id')))
    offer = Offer.objects.filter(item=items.values('id'))

    of = Offer.objects.filter(
        type_transaction=OfferCnoice.SELL.value, is_active=True,
        price_gt=0
    )


@query_debugger
def ex111():
    # items = Item.objects.filter(item_offer=OuterRef('id'))
    # offer = Offer.objects.filter(item=Subquery(items.values('id')))

    # price = Price.objects.filter(item=OuterRef('id'))
    # offer = Offer.objects.filter(item__item_price__price=Subquery(price.values('id')))
    # offer = Offer.objects.filter(price__gt=F('item__item_price__price'))

    offer = Offer.objects.select_related('item').filter(price__gt=F('item__item_price__price'))  # +
    offers = offer.annotate(difference=F('item__item_price__price') - F('price'))
    print(offers)


@query_debugger
def ex6():
    '''
    recent_comments = Comment.objects.filter(
    ...     post=OuterRef('pk'),
    ...     created_at__gte=one_day_ago,
    ... )
    Post.objects.annotate(recent_comment=Exists(recent_comments))
    '''
    # offers = Offer.objects.filter(is_active=True)
    offers = Offer.objects.filter(item=OuterRef('id'), is_active=True)
    item = Item.objects.annotate(offer_active=Exists(offers))  # offer_active = boolean
    item.filter(offer_active=True)  # 0.000982s
    print(item)


def ex7():
    '''
    если оффер для покупки
    '''
    buy_offer = Offer.objects.annotate(type=Case(
        When(Q(type_transaction=OfferCnoice.BUY.value) & Q(is_active=True),
             then=Value('for buy'))))
    buy_offer.filter(type__isnull=False)
    buy_offer = Offer.objects.annotate(
        type=Case(When(type_transaction=OfferCnoice.BUY.value, then=Value('for buy')))).filter(type__isnull=False)
    print(buy_offer)


def ex8():
    '''
    все акциий с группировкой по user
    SELECT "trading_offer"."user_id",
       COUNT("trading_offer"."id") AS "count_off"
    FROM "trading_offer"
    WHERE ("trading_offer"."type_transaction" = 'SELL' AND "trading_offer"."is_active")
    GROUP BY "trading_offer"."user_id"
    '''
    off = Offer.objects.filter(user=OuterRef('id'), item=OuterRef('id')).values('id')
    item = Item.objects.annotate(items=Exists(off))
    item = Item.objects.filter(item_offer__in=Exists(off))

    off = Offer.objects.values('user') \
        .filter(Q(type_transaction=OfferCnoice.SELL.value)) \
        .annotate(count_off=Count('id')).values('id')

    #  faster
    off = Offer.objects.values('user') \
        .annotate(count_off=Count('id', filter=Q(type_transaction=OfferCnoice.SELL.value)))

    off = Offer.objects.values('user') \
        .filter(Q(type_transaction=OfferCnoice.SELL.value)) \
        .annotate(count_off=Count('id')).values('id')

    it = Item.objects.filter(
        item_offer__id__in=Exists(off))
