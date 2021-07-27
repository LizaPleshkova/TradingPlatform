from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from requests import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer, OfferDetailSerializer, ItemDetailSerializer, \
    TradeDetailSerializer, InventoryDetailSerializer, \
    InventorySerializer, PriceDetailSerializer, CurrencyDetailSerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile
from .services import TradeService, OfferService, BaseService, ProfitableTransactionsServices

User = get_user_model()


class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet, OfferService):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        # queryset = Offer.objects.filter(user=self.request.user)
        queryset = Offer.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return OfferDetailSerializer
        return OfferListSerializer

    def create(self, request, *args, **kwargs):
        try:
            print(request.data)
            serializer, offer_data = self.get_validate_data(request)
        except serializers.ValidationError as e:
            return Response(e.detail['non_field_errors'], status=status.HTTP_400_BAD_REQUEST)
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
        return InventorySerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CurrencyView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Currency.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return CurrencyDetailSerializer
        return CurrencySerializer


class PriceView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Price.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return PriceDetailSerializer
        return PriceSerializer


class TradeView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet,
                TradeService, BaseService):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # queryset = Trade.objects.filter(buyer=self.request.user)
        queryset = Trade.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return TradeDetailSerializer
        return TradeSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer, data = self.get_validate_data(request)
            buyer_user = data.get('buyer')
            seller_user = data.get('seller')
            buyer_offer = data.get('buyer_offer')
            seller_offer = data.get('seller_offer')

            # updating fields buyer
            TradeService.updating_user_score(buyer_user, buyer_offer)
            TradeService.updating_inventory_buyer(buyer_user, buyer_offer)

            # updating field seller
            TradeService.updating_user_score(seller_user, seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_user, seller_offer, buyer_offer)

            TradeService.updating_price_item(buyer_offer)

            # save trade
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ObjectDoesNotExist as e:
            # print(getattr(e, 'message', repr(e)))
            # print(dir(repr(e).title().), repr(e).title())
            return Response(getattr(e, 'message', repr(e)), status=status.HTTP_400_BAD_REQUEST)


class ProfitableTransactions(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TradeDetailSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Offer.objects.filter(user=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            ProfitableTransactionsServices.requirements_for_transaction()
            # out_offers = task.requirements_transaction.delay(user)
            return Response(status=status.HTTP_200_OK)
            # return JsonResponse(out_offers, safe=False)
        except BaseException as e:
            return Response(getattr(e, 'message', repr(e)), status=status.HTTP_400_BAD_REQUEST)
