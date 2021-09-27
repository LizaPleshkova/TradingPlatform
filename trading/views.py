import json
import django_filters
import stripe
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F
from django.utils.datastructures import MultiValueDictKeyError
from requests import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    ItemSerializer, WatchListSerializer, CurrencySerializer, PriceSerializer,
    OfferDetailSerializer, ItemDetailSerializer, TradeDetailSerializer, InventoryDetailSerializer, InventorySerializer,
    PriceDetailSerializer, CurrencyDetailSerializer, PopularItemSerializer, OfferRetrieveSerializer,
)
from .models import Currency, Item, Price, WatchList, Offer, Inventory
from trading.services import (import_export_excel, import_export_csv, payment, statistics, trade, )

User = get_user_model()


class ImportExportCsvView(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['post'], detail=False, url_path='import')
    def import_from_csv(self, request):
        try:
            excel_file = request.FILES['file'].name
            print(excel_file)
            data = import_export_csv.ImportCsv.import_from_csv(excel_file)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='export')
    def export_to_csv(self, request):
        try:
            excel_file = request.FILES['file'].name
            data = import_export_csv.ExportCsv.export_to_csv(excel_file)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ImportExportExcelView(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['post'], detail=False, url_path='import-currencies')
    def import_method(self, request):
        try:
            excel_file = request.FILES['file'].name
            data = import_export_excel.ImportExcelService.import_currency_to_excel(excel_file)
            return Response(data, status=status.HTTP_200_OK)
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValueError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='import')
    def import_sheets(self, request):
        try:
            data = import_export_excel.ImportExcelService.import_excel_sheets(
                request.FILES['file'].name
            )
            return Response(data, status=status.HTTP_200_OK)
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValueError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='export')
    def export_to_excel(self, request):
        try:
            excel_file = request.FILES['file'].name
            data = import_export_excel.ExportExcelService.export_to_excel(excel_file)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PaymentView(ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['get'], detail=False, url_path='payment-method')
    def payment_method(self, request):
        payment_method = payment.PaymentService.create_payment_method_card(request)
        return Response(payment_method, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='confirm-payment')
    def confirm_payment(self, request):
        conf = payment.PaymentService.confirm_payment_intent(request)
        return Response(conf, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='payment')
    def create_payment_intent(self, request):
        s = payment.PaymentService.create_payment_intent(request)
        return Response(s, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='secret')
    def secret(self, request):
        test_payment_intent = stripe.PaymentIntent.retrieve(
            request.data.get("payment_intent_id")
        )
        return Response(data=test_payment_intent.client_secret, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='customer-list')
    def customer_list(self, request):
        test_payment_intent = stripe.PaymentMethod.list()
        return Response(data=test_payment_intent, status=status.HTTP_200_OK)


class StatisticViews(ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        ''' general statistic '''
        ser_data = statistics.StatisticService.users_statistic(self.request.user.id)
        return Response(ser_data, status=status.HTTP_200_OK, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='popular-objects')
    def popular_objects(self, request):
        ser_data = statistics.StatisticService.get_popular_objects()
        return Response(ser_data, status=status.HTTP_200_OK, content_type="application/json")

    @action(methods=['get'], detail=False, url_path='user-trade-today')
    def user_trade_today(self, request):
        tr = statistics.StatisticService.user_trade_today_count(request.user.id)
        return Response(tr, content_type="application/json", status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='user-items-today')
    def user_items_todays(self, request):
        # tr = StatisticService.items_today_second(request.user)
        tr = statistics.StatisticService.items_today(request.user.id)
        return Response(tr, content_type="application/json", status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='user-items-today-sec')
    def user_items_today(self, request):
        tr = statistics.StatisticService.items_today_second(request.user)
        # tr = StatisticService.items_today(request.user.id)
        return Response(tr, content_type="application/json", status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='sum-trade-today')
    def sum_trade_today(self, request):
        tr = statistics.StatisticService.sum_user_trade_today(request.user.id)
        return Response(tr, content_type="application/json", status=status.HTTP_200_OK)


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
        return Response(json_offer, content_type="text/json-comment-filtered", status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='price_offers_users')
    def price_offers_users(self, request):
        offers = Offer.objects.values('user').annotate(sum_offers=Sum(F('price') * F('quantity')))
        for off in offers:
            off['sum_offers'] = float(off['sum_offers'])
        return Response(json.dumps(list(offers)), content_type="application/json", status=status.HTTP_200_OK)


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
        return Response(m.data, content_type='application/json', status=status.HTTP_200_OK)


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
            trade.ProfitableTransactionsServices.requirements_for_transaction()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response(getattr(e, 'message', repr(e)), status=status.HTTP_400_BAD_REQUEST)
