from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from trading.models import Currency, Item, Price, WatchList, Offer, Inventory, OfferCnoice

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
    currency1 = Currency.objects.create(code='AAPLE', name='apple')
    currency2 = Currency.objects.create(code='lll', name='lll')
    item1 = Item.objects.create(code='aaple1', name='apple1', currency=currency1)
    price1 = Price.objects.create(item=item1, currency=currency1, price=10)

    return {
        "currency1": currency1,
        "currency2": currency2,
        "item": item1,
        "price": price1
    }


@pytest.fixture
def offer_inventory_setup(user1_setup, user2_setup, service_setup):
    inventory1 = Inventory.objects.create(item=service_setup['item'], user=user1_setup, quantity=0)
    inventory2 = Inventory.objects.create(item=service_setup['item'], user=user2_setup, quantity=0)
    watchlist = WatchList.objects.create(user=user1_setup, item=service_setup['item'])
    offer1 = Offer.objects.create(
        type_transaction=OfferCnoice.BUY.name,
        item=service_setup['item'],
        user=user1_setup,
        price=100,
        quantity=2,
    )
    offer2 = Offer.objects.create(
        type_transaction=OfferCnoice.SELL.name,
        item=service_setup['item'],
        user=user2_setup,
        price=100,
        quantity=10,
    )
    offer3 = Offer.objects.create(
        type_transaction=OfferCnoice.BUY.name,
        item=service_setup['item'],
        user=user2_setup,
        price=100,
        quantity=20,
    )

    return {
        "user1": user1_setup,
        "user2": user2_setup,
        "offer1": offer1,
        "offer2": offer2,
        "offer3": offer3,
        "watchlist": watchlist,
        "inventory1": inventory1,
        "inventory2": inventory2
    }


@pytest.fixture
def api_client1(user1_setup):
    client = APIClient()
    refresh = RefreshToken.for_user(user1_setup)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return {
        "client": client,
        "user": user1_setup
    }


@pytest.fixture
def api_client2(user2_setup):
    client = APIClient()
    refresh = RefreshToken.for_user(user2_setup)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return {
        "client": client,
        "user": user1_setup
    }


# @pytest.fixture(scope="module")
@pytest.fixture
def user1_setup():
    user = User.objects.create(username='user1', password='user1123')
    return user


# @pytest.fixture(scope="module")
@pytest.fixture
def user2_setup():
    user = User.objects.create(username='user2', password='user2123')
    return user
