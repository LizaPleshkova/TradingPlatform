import pytest
from django.test.client import Client
from pytest_django.lazy_django import skip_if_no_django
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import pytest
import mixer
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

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


@pytest.fixture
def service_setup():
    # print(signals_setup)
    # user1 = signals_setup
    # print(user1)
    # user2 = User.objects.get(id=1)
    # user1 = User.objects.create(username='admin', password=123)
    currency1 = Currency.objects.create(code='AAPLE', name='apple')
    currency2 = Currency.objects.create(code='lll', name='lll')
    item1 = Item.objects.create(code='aaple1', name='apple1', currency=currency1)
    price1 = Price.objects.create(item=item1, currency=currency1, price=120)
    # offer1 = Offer.objects.create(
    #     type_transaction=OfferCnoice.BUY.name,
    #     item=item1,
    #     user=user1,
    #     price=100,
    #     quantity=2,
    # )
    # offer1 = Offer.objects.create(
    #     type_transaction=OfferCnoice.BUY.name,
    #     item=item1,
    #     user=user1,
    #     price=100,
    #     quantity=2,
    # )
    # inventory1 = Inventory.objects.create(item=item1, user=user1, quantity=2)
    return currency1, item1, price1


@pytest.fixture
def api_client1():
    user = User.objects.create_user(username='john', email='js@js.com', password='123')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def inventory_setup(service_setup):
    user2 = User.objects.get(id=2)
    inventory1 = Inventory.objects.create(item=service_setup[1], user=user2, quantity=0)
    return inventory1


@pytest.fixture
def api_client2():
    user = User.objects.create_user(username='john', email='js@js.com', password='123')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# @pytest.fixture
# def api_client():
#     user = User.objects.create_user(username='admin', password=123)
#     client = APIClient()
#     refresh = RefreshToken.for_user(user)
#     client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
#     return client
#

@pytest.fixture
def user1_setup():
    user = User.objects.create(username='john', email='js@js.com', password='123')
    return user


@pytest.fixture
def user2_setup():
    user = User.objects.create(username='john', email='js@js.com', password='123')
    return user


@pytest.fixture
def api_fact(user_setup):
    user = User.objects.create_user(username='john', email='js@js.com', password='123')
    factory = APIRequestFactory()
    refresh = RefreshToken.for_user(user_setup)
    # token, created = Token.objects.get_or_create(user=self.user)
    # client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return factory

# @pytest.fixture
# def auth_token(api_fact):
#     token, created = Token.objects.get_or_create()
