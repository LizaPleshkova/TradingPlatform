import json

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.test.client import Client
from django.urls import reverse
from pytest_django.lazy_django import skip_if_no_django
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import pytest
from rest_framework import status, serializers

from rest_framework.test import APIClient, APIRequestFactory
from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer, CurrencyDetailSerializer, OfferDetailSerializer
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile, OfferCnoice
from trading.services import TradeService, OfferService, BaseService, ProfitableTransactionsServices
from trading.services import TradeService, OfferService, BaseService, ProfitableTransactionsServices, \
    _updating_offer_quantity, _updating_offer_is_active
from trading.views import OfferListUserView, ItemView, WatchListView, InventoryView, \
    PriceView, CurrencyView, TradeView, ProfitableTransactions

User = get_user_model()


# @pytest.mark.django_db
# def test_serializer_offer_seller_invalid(user2_setup, service_setup):
#     ''' invalid, when sell  and  seller's inventory DoesNotExist'''
#     inv = Inventory.objects.all()
#     assert len(inv) == 0
#
#     data = {
#         "user": user2_setup.id,
#         "type_transaction": "SELL",
#         "item": 1,
#         "price": 10,
#         "quantity": 10
#     }
#
#     with pytest.raises(ObjectDoesNotExist) as e:
#         serializer = OfferDetailSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#     assert str(e.value) == 'No Inventory seller matches the given query'

@pytest.mark.django_db
def test_serializer_offer_seller_invalid(user2_setup, service_setup, inventory_setup):
    ''' invalid, when sell and inventory_seller.quantity <= data.get('quantity')'''
    inv = Inventory.objects.all().first()
    assert inv.quantity == 0

    data = {
        "user": user2_setup.id,
        "type_transaction": "SELL",
        "item": 1,
        "price": 10,
        "quantity": 10
    }

    with pytest.raises(serializers.ValidationError) as e:
        serializer = OfferDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)

#
# FAILED test\test_services\test_serializer.py::test_serializer_offer_seller_valid - rest_framework.exceptions.ValidationError: {'item': [ErrorDetail(string='Недопустимый первичный ключ "1" - объект не существует...
#
# ERROR test\test_services\test_serializer.py::test_serializer_offer_seller_invalid - django.contrib.auth.models.User.DoesNotExist: User matching query does not exist.

@pytest.mark.django_db
def test_serializer_offer_seller_invalid(user1_setup, service_setup, inventory_setup):
    ''' invalid, when buy and buyer_profile.score <= (data.get('quantity') * data.get('price'))'''
    profile = UserProfile.objects.get(id=user1_setup.id)
    assert profile.score == 0

    data = {
        "user": user1_setup.id,
        "type_transaction": "BUY",
        "item": 1,
        "price": 10,
        "quantity": 10
    }

    with pytest.raises(serializers.ValidationError) as e:
        serializer = OfferDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_serializer_offer_seller_valid(user1_setup, service_setup, inventory_setup):
    ''' invalid, when buy and buyer_profile.score <= (data.get('quantity') * data.get('price'))'''
    profile = UserProfile.objects.get(id=user1_setup.id)

    assert profile.score == 0

    profile.score = 1000
    profile.save(update_fields=["score"])

    assert profile.score == 1000

    data = {
        "user": user1_setup.id,
        "type_transaction": "BUY",
        "item": 1,
        "price": 10,
        "quantity": 10
    }

    serializer = OfferDetailSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    assert serializer.validated_data == data