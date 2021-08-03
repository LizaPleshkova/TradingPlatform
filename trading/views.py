from django.contrib.auth import get_user_model
from requests import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    OfferListSerializer, ItemSerializer, WatchListSerializer, CurrencySerializer, PriceSerializer,
    OfferDetailSerializer, ItemDetailSerializer, TradeDetailSerializer, InventoryDetailSerializer, InventorySerializer,
    PriceDetailSerializer, CurrencyDetailSerializer
)
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory
from .services import ProfitableTransactionsServices

User = get_user_model()


class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Offer.objects.all()

    serializer_classes_by_action = {
        'retrieve': OfferDetailSerializer,
        'create': OfferDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, OfferListSerializer)

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


class ItemView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()

    serializer_classes_by_action = {
        'retrieve': ItemDetailSerializer,
        'create': ItemDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, ItemSerializer)


class WatchListView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WatchListSerializer

    def get_queryset(self, *args, **kwargs):
        return WatchList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class InventoryView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Inventory.objects.filter(user=self.request.user)

    serializer_classes_by_action = {
        'retrieve': InventoryDetailSerializer,
        'create': InventoryDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes_by_action.get(self.action, InventorySerializer)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


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
