from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from .serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, InventorySerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from .models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile
from rest_framework import generics
from decimal import Decimal
from .services import TradeService

User = get_user_model()


# class OfferList(ListModelMixin, RetrieveModelMixin, CreateModelMixin, generics.GenericAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = OfferListSerializer
#     queryset = Offer.objects.all()
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request)
#

class OfferListUserView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferListSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('type_transaction') == 'SELL':
            try:
                inventory_seller = Inventory.objects.get(user=self.request.user,
                                                         item=serializer.validated_data.get('item'))
                if inventory_seller.quantity < serializer.validated_data.get('quantity'):
                    return Response({'You want to sell more stocks than you have'}, status=status.HTTP_400_BAD_REQUEST)
            except Inventory.DoesNotExist:
                return Response({"No Inventory seller matches the given query."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self, *args, **kwargs):
        queryset = Offer.objects.filter(user=self.request.user)
        return queryset


class ItemView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


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
    serializer_class = InventorySerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Inventory.objects.filter(user=self.request.user)
        return queryset

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


class TradeView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, viewsets.GenericViewSet, TradeService):
    permission_classes = (IsAuthenticated,)
    serializer_class = TradeSerializer

    def get_queryset(self):
        queryset = Trade.objects.filter(buyer=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        buyer_user = serializer.validated_data.get('buyer')
        seller_user = serializer.validated_data.get('seller')
        buyer_offer = serializer.validated_data.get('buyer_offer')
        seller_offer = serializer.validated_data.get('seller_offer')
        print(buyer_user, seller_user, buyer_offer, seller_offer)

        # 3
        user_profile = self.updating_user_score(buyer_user, buyer_offer)
        inventory_buyer = self.updating_inventory_buyer(buyer_user, buyer_offer)

        # 4
        seller_profile = self.updating_user_score(seller_user, seller_offer, buyer_offer)
        inventory_seller = self.updating_inventory_seller(seller_user, seller_offer, buyer_offer)

        # # 5
        # updating price stock
        price_item = buyer_offer.item.price_item.get()
        price_item.price += Decimal(buyer_offer.price) * Decimal(0.01)
        price_item.save()

        # save trade
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
