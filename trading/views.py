from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from . import serializers
from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer, OfferDetailSerializer, ItemDetailSerializer, \
    TradeDetailSerializer, InventoryDetailSerializer, \
    InventorySerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile
from .services import TradeService, OfferService, BaseService

User = get_user_model()


class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet, OfferService):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        queryset = Offer.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return OfferDetailSerializer
        return OfferListSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer, offer_data = self.get_validate_data(request)
            # OfferService.checking_quantity_stocks_seller(offer_data)
        except serializers.ValidationError:
            return Response({'You want to sell more stocks than you have'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"No Inventory seller matches the given query."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(offer_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ItemView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return ItemDetailSerializer
        return ItemSerializer


class WatchListView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WatchListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = WatchList.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class InventoryView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        queryset = Inventory.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryDetailSerializer
        # elif self.action == 'create':
        #     return InventoryCreateSerializer
        return InventorySerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CurrencyView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()


class PriceView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PriceSerializer
    queryset = Price.objects.all()


class TradeView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                TradeService, BaseService):
    permission_classes = (IsAuthenticated,)
    serializer_class = TradeSerializer

    def get_queryset(self):
        queryset = Trade.objects.filter(buyer=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TradeDetailSerializer
        # elif self.action == 'create':
        #     return
        return TradeSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer, data = self.get_validate_data(request)

            buyer_user = data.get('buyer')
            seller_user = data.get('seller')
            buyer_offer = data.get('buyer_offer')
            seller_offer = data.get('seller_offer')
            # print('buyer', buyer_user, '--', seller_user, buyer_offer, seller_offer)

            # 3
            # updating fields buyer
            TradeService.updating_user_score(buyer_user, buyer_offer)
            TradeService.updating_inventory_buyer(buyer_user, buyer_offer)

            # 4
            # updating field seller
            seller_profile = TradeService.updating_user_score(seller_user, seller_offer, buyer_offer)
            inventory_seller = TradeService.updating_inventory_seller(seller_user, seller_offer, buyer_offer)

            # 5
            TradeService.updating_price_item(buyer_offer)

            # save trade
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
