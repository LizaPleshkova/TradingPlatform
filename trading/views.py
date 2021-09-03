import json
import django_filters
import stripe
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F
from django.http import JsonResponse, HttpResponse
from requests import Response
from rest_framework.decorators import api_view, action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from django.core.exceptions import ObjectDoesNotExist
# from statistic.models import Statistic
from TradingPlatform import settings
from .serializers import (
    OfferListSerializer, ItemSerializer, WatchListSerializer, CurrencySerializer, PriceSerializer,
    OfferDetailSerializer, ItemDetailSerializer, TradeDetailSerializer, InventoryDetailSerializer, InventorySerializer,
    PriceDetailSerializer, CurrencyDetailSerializer, PopularItemSerializer, OfferRetrieveSerializer,
)
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, Ip
from .services import ProfitableTransactionsServices, get_client_ip, StatisticService
from django.core import serializers

User = get_user_model()


class PaymentView(ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['get'], detail=False, url_path='payment')
    def payment(self, request):
        test_payment_intent = stripe.PaymentIntent.create(
            amount=1000,
            currency='eur',
            payment_method_types=['card'],
            receipt_email='pl.1.el.vas@gmail.com',

            # customer=stripe.Customer.retrieve("cus_K9x9PqOTWgP0X6")
        )
        intent_list = stripe.PaymentIntent.list()
        # #
        # for i in intent_list:
        #     stripe.PaymentIntent.cancel(
        #         i['id']
        #     )
        return Response(data=intent_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='customers')
    def customers(self, request):
        customer = stripe.Customer.create(
            email='pl.1.el.vas@gmail.com',
            stripe_account=settings.STRIPE_ACCOUNT_ID,
            name='liza'
        )
        customer_list = stripe.Customer.list()
        # cust_update = stripe.Customer.modify(
        #     'cus_K9vfIysK78Uw3L',
        #     name='liza'
        # )
        # stripe.Customer.delete('cus_K9wHGDkjOW7eVA')
        # stripe.Customer.delete('cus_K9wHudrM0HVYpB')
        # # stripe.Customer.delete('cus_K9wIDUfLXyHpJ5')
        # stripe.Customer.delete('cus_K9wI5CepLnpCLh')
        # stripe.Customer.delete('cus_K9wJKvot5u6mgp')
        return Response(data=(customer_list), status=status.HTTP_200_OK)


    @action(methods=['get'], detail=False, url_path='accounts')
    def accounts(self, request):
        # customer = stripe.Account.create(
        #     email='pl.1.el.vas@gmail.com',
        #     stripe_account=settings.STRIPE_ACCOUNT_ID,
        # )
        account_list = stripe.Account.list()
        # account = stripe.Account.create(
        #     type="custom",
        #     country="US",
        #     email='pl.1.el.vas@gmail.com',
        #     # capabilities={
        #     #     "card_payments": {"requested": True},
        #     #     "transfers": {"requested": True},
        #     # },
        # )

        return Response(data=account_list, status=status.HTTP_200_OK)


class StatisticViews(ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        ''' general statistic '''
        ser_data = StatisticService.users_statistic(self.request.user.id)
        return Response(ser_data, status=status.HTTP_200_OK, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='popular-objects')
    def popular_objects(self, request):
        # +
        ser_data = StatisticService.get_popular_objects()
        return Response(ser_data, status=status.HTTP_200_OK, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='user-trade-today')
    def user_trade_today(self, request):
        tr = StatisticService.user_trade_today_count(self.request.user.id)
        return Response(tr, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='user-items-today')
    def user_items_today(self, request):
        tr = StatisticService.items_today(self.request.user.id)
        return Response(tr, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='sum-trade-today')
    def sum_trade_today(self, request):
        ''' не работает - из--за высчитывания сумымы'''
        tr = StatisticService.sum_user_trade_today(self.request.user.id)
        return Response(tr, content_type="application/json")


class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_classes_by_action = {
        'retrieve': OfferRetrieveSerializer,
        'create': OfferDetailSerializer,
    }
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'is_active']

    def get_queryset(self, *args, **kwargs):
        return Offer.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, OfferRetrieveSerializer)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ip = get_client_ip(request)
        ip = '0.0.0.1'
        serializer = self.get_serializer(instance)
        if Ip.objects.filter(ip=ip).exists():
            instance.counts_views.add(Ip.objects.get(ip=ip))
        else:
            Ip.objects.create(ip=ip)
            instance.counts_views.add(Ip.objects.get(ip=ip))

        # instance.counts_views += 1
        # instance.save(update_fields=["counts_views"])
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            request.data['user'] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ObjectDoesNotExist as e:
            return Response(getattr(e, 'message', repr(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='price_offers')
    def price_offer_user(self, request):
        offers = Offer.objects.filter(user=request.user).aggregate(sum_offers=Sum(F('price') * F('quantity')))
        offers['sum_offers'] = float(offers['sum_offers'])
        json_offer = json.dumps(offers)
        return Response(json_offer, content_type="text/json-comment-filtered")

    @action(methods=['get'], detail=False, url_path='price_offers_users')
    def price_offers_users(self, request):
        offers = Offer.objects.values('user').annotate(sum_offers=Sum(F('price') * F('quantity')))
        for off in offers:
            off['sum_offers'] = float(off['sum_offers'])
        return Response(json.dumps(list(offers)), content_type="application/json")

    @action(methods=['get'], detail=False, url_path='popular-offer')
    def popular_offer(self, request):
        offers = Offer.objects.values('id').annotate(co=Count('counts_views')).order_by('-co').first()
        offers = Offer.objects.annotate(co=Count('counts_views')).order_by('-co').first()

        return Response(json.dumps(offers), content_type="application/json")


class ItemView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['currency']

    serializer_classes_by_action = {
        'retrieve': ItemDetailSerializer,
        'create': ItemDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, ItemSerializer)

    @action(methods=['get'], detail=False)
    def popular_item(self, request):
        item = Item.objects.annotate(count_offers=Count('item_offer')).order_by('-count_offers')[:1]
        m = PopularItemSerializer(item, many=True)
        # nb = json.dumps(m.data)
        return HttpResponse(m.data, content_type='application/json')


class WatchListView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WatchListSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'item', ]

    def get_queryset(self, *args, **kwargs):
        return WatchList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class InventoryView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'item', ]
    serializer_classes_by_action = {
        'retrieve': InventoryDetailSerializer,
        'create': InventorySerializer,
        'list': InventorySerializer,
    }

    def get_queryset(self, *args, **kwargs):
        return Inventory.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, InventorySerializer)

    # def perform_create(self, serializer):
    #     return serializer.save(user=self.request.user)


class CurrencyView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Currency.objects.all()
    serializer_classes_by_action = {
        'retrieve': CurrencyDetailSerializer,
        'create': CurrencyDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, CurrencySerializer)


class PriceView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Price.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['user', 'item', ]

    serializer_classes_by_action = {
        'retrieve': PriceDetailSerializer,
        'create': PriceDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, PriceSerializer)


class ProfitableTransactions(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TradeDetailSerializer

    def get_queryset(self, *args, **kwargs):
        return Offer.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            ProfitableTransactionsServices.requirements_for_transaction()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response(getattr(e, 'message', repr(e)), status=status.HTTP_400_BAD_REQUEST)
