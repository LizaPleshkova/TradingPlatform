import pytest
from django.test.client import Client
from pytest_django.lazy_django import skip_if_no_django
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import pytest

from rest_framework.test import APIClient, APIRequestFactory
from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile, OfferCnoice
from trading.services import TradeService, OfferService, BaseService, ProfitableTransactionsServices

User = get_user_model()


@pytest.fixture()
def api_client():
    """A Django RestFramework test client instance."""

    return APIClient()


@pytest.fixture()
def api_rf():
    """A Django RestFramework RequestFactory instance"""

    return APIRequestFactory()


#
@pytest.fixture
def service_setup():
    user1 = User.objects.create(username='admin', password1=123, password2=123)
    currency1 = Currency.objects.create(code='AAPLE', name='apple')
    item1 = Item.objects.create(code='aaple1', name='apple1', currency=currency1)
    price1 = Price.objects.create(item=item1, currency=currency1, price=120)
    offer1 = Offer.objects.create(
        type_transaction=OfferCnoice.BUY.name,
        item=item1,
        user=user1,
        price=100,
        quantity=2,
    )
    inventory1 = Inventory.objects.create(item=item1, user=user1, quantity=2)
    return currency1, item1, price1, offer1, inventory1
