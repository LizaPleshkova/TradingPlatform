from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, InventorySerializer, \
    CurrencySerializer, PriceSerializer
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory
from rest_framework import generics


class OfferList(ListModelMixin, RetrieveModelMixin, CreateModelMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferListSerializer
    queryset = Offer.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request)


class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                        generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferListSerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_queryset(self, *args, **kwargs):
        queryset = Offer.objects.filter(user=self.request.user)
        return queryset


class ItemView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
               generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class WatchListView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                    generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WatchListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = WatchList.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class InventoryView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                    generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = InventorySerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Inventory.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CurrencyView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()


class PriceView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PriceSerializer
    queryset = Price.objects.all()

