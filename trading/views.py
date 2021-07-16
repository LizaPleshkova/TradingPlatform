from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, InventorySerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile
from rest_framework import generics

from trading.services import TradeService

User = get_user_model()


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


class TradeView(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet,
                generics.GenericAPIView, TradeService):
    permission_classes = (IsAuthenticated,)
    serializer_class = TradeSerializer
    queryset = Trade.objects.all()

    def get_queryset(self):
        queryset = Trade.objects.filter(buyer=self.request.user)
        return queryset


    def post(self, request, *args, **kwargs):
        '''
        1цена покупки <= числа продаж
        2кол-во акций для покупки <= кол-во акций для продаж

        3у того, кто покупает -- снимаются деньги со счета + добавляются акции в inventory
        4у того, кто продает -- добавляются деньги за акции на счет + списываются конкретные акции из Inventory
        5изменяется цена акции после сделки
        '''

        buyer_user_id = self.request.data.get('buyer')
        seller_user_id = self.request.data.get('seller')
        buyer_offer = self.request.data.get('buyer_offer')
        seller_offer = self.request.data.get('seller_offer')
        description = self.request.data.get('description')

        # get objects
        buyer_user = get_object_or_404(User, id=buyer_user_id)
        seller_user = get_object_or_404(User, id=seller_user_id)
        buyer_offer = get_object_or_404(Offer, id=buyer_offer)
        seller_offer = get_object_or_404(Offer, id=seller_offer)

        # 3
        user_profile = self.updating_user_score(buyer_user_id, buyer_offer)
        self.updating_inventory_buyer(buyer_user,buyer_offer)

        # 4
        seller_profile = self.updating_user_score(seller_user_id, seller_offer, buyer_offer)
        self.updating_inventory_seller(seller_user, seller_offer)

        # # 5
        # price = buyer_offer.item.price_item
        # print(price)

        # save trade
        trade = Trade.objects.create(
            buyer=buyer_user,
            seller=seller_user,
            buyer_offer=buyer_offer,
            seller_offer=seller_offer,
            description=description

        )

        serializer = self.get_serializer(trade)
        return Response(serializer.data, status=status.HTTP_200_OK)
