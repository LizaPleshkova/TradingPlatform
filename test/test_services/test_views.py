import datetime
import json
from django.contrib.auth import get_user_model
import pytest
from rest_framework import status
from trading.serializers import (
    ItemSerializer, WatchListSerializer, CurrencySerializer, PriceSerializer, CurrencyDetailSerializer,
    InventorySerializer, PriceDetailSerializer, ItemDetailSerializer
)
from trading.models import Currency, Item, Price, WatchList, Inventory, UserProfile

User = get_user_model()


# currency
@pytest.mark.django_db
def test_get_currencies(api_client1, service_setup):
    response = api_client1['client'].get('/trading/currency/')
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many=True)
    response_content = json.loads(response.content.decode('utf-8'))
    assert serializer.data == response_content
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_currency(api_client1, service_setup):
    response = api_client1['client'].get('/trading/currency/{0}/'.format(service_setup['currency1'].id))

    currency1 = Currency.objects.get(id=service_setup['currency1'].id)
    serializer = CurrencyDetailSerializer(currency1)

    response_content = json.loads(response.content.decode('utf-8'))

    assert serializer.data == response_content
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_currency(api_client1, service_setup):
    data = {"code": "USD", "name": "Usd"}
    response = api_client1['client'].post('/trading/currency/', data, format='json')
    currency1 = Currency.objects.all().last()
    serializer = CurrencyDetailSerializer(currency1)
    response_content = json.loads(response.content.decode('utf-8'))
    assert serializer.data == response_content
    assert response.status_code == status.HTTP_201_CREATED


# offer
@pytest.mark.django_db
def test_create_offer_valid(api_client1, offer_inventory_setup, service_setup):
    ''' invalid, when sell and inventory_seller.quantity <= data.get('quantity')'''
    profile = UserProfile.objects.get(user=api_client1['user'].id)
    assert profile.score == 0

    profile.score = 1000
    profile.save(update_fields=["score"])

    assert profile.score == 1000
    data = {
        "type_transaction": "BUY",
        "item": service_setup['item'].id,
        "price": 5,
        "quantity": 10
    }
    response = api_client1["client"].post('/trading/user-offers/', data, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_offer_invalid1(api_client2, service_setup):
    ''' invalid, when inventory seller sell '''
    inv = Inventory.objects.all()
    assert len(inv) == 0
    data = {
        "type_transaction": "SELL",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }
    response = api_client2['client'].post('/trading/user-offers/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_offer_invalid2(api_client2, service_setup):
    inv = Inventory.objects.all()
    assert len(inv) == 0
    data = {
        "type_transaction": "SELL",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }
    response = api_client2['client'].post('/trading/user-offers/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# inventory
@pytest.mark.django_db
def test_get_inventories(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/inventory/', format='json')
    inventories = Inventory.objects.filter(user=api_client1['user'])
    assert len(inventories) != 0

    serializer = InventorySerializer(inventories, many=True)
    response_content = json.loads(response.content.decode('utf-8'))
    assert serializer.data == response_content
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_inventory(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/inventory/{0}/'.format(offer_inventory_setup['inventory1'].id))
    inventory = Inventory.objects.get(id=offer_inventory_setup['inventory1'].id)
    assert inventory != None
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_inventory(api_client1, service_setup, offer_inventory_setup):
    assert len(Inventory.objects.all()) == 2
    data = {
        "item": service_setup['item'].id,
        "quantity": 10
    }
    response = api_client1['client'].post('/trading/inventory/', data, format='json')
    assert len(Inventory.objects.all()) == 3
    assert response.status_code == status.HTTP_201_CREATED


# watch-list
@pytest.mark.django_db
def test_get_watchlist(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/watch-list/', format='json')
    watchlist = WatchList.objects.filter(user=api_client1['user'])
    assert len(watchlist) == 1

    serializer = WatchListSerializer(watchlist, many=True)
    response_content = json.loads(response.content.decode('utf-8'))
    assert serializer.data == response_content
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_watchlist(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/watch-list/{0}/'.format(offer_inventory_setup['watchlist'].id))
    watchlist = WatchList.objects.get(id=offer_inventory_setup['watchlist'].id)
    assert watchlist != None
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_watchlist(api_client2, service_setup, offer_inventory_setup):
    assert len(WatchList.objects.all()) == 1
    data = {
        "item": service_setup['item'].id,
    }
    response = api_client2['client'].post('/trading/watch-list/', data, format='json')
    assert len(WatchList.objects.all()) == 2
    assert response.status_code == status.HTTP_201_CREATED


# price
@pytest.mark.django_db
def test_get_prices(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/price/', format='json')
    prices = Price.objects.all()
    assert len(prices) == 1

    serializer = PriceSerializer(prices, many=True)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_price(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/price/{0}/'.format(service_setup['price'].id))
    price = Price.objects.get(id=service_setup['price'].id)

    serializer = PriceDetailSerializer(price)
    response_content = json.loads(response.content.decode('utf-8'))
    assert response.status_code == status.HTTP_200_OK
    assert serializer.data == response_content


@pytest.mark.django_db
def test_create_inventory(api_client1, service_setup, offer_inventory_setup):
    assert len(Price.objects.all()) == 1
    data = {
        "item": service_setup['item'].id,
        "price": 121,
        "currency": service_setup['currency1'].id,
        "data": datetime.datetime.now()
    }
    response = api_client1['client'].post('/trading/price/', data, format='json')
    assert len(Price.objects.all()) == 2
    assert response.status_code == status.HTTP_201_CREATED


# item
@pytest.mark.django_db
def test_get_items(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/item/', format='json')
    items = Item.objects.all()
    assert len(items) == 1

    serializer = ItemSerializer(items, many=True)
    response_content = json.loads(response.content.decode('utf-8'))
    print(response_content)
    assert serializer.data == response_content
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_item(api_client1, service_setup, offer_inventory_setup):
    response = api_client1['client'].get('/trading/item/{0}/'.format(service_setup['item'].id))
    price = Item.objects.get(id=service_setup['item'].id)

    serializer = ItemDetailSerializer(price)
    response_content = json.loads(response.content.decode('utf-8'))
    print(response_content)
    assert response.status_code == status.HTTP_200_OK
    assert serializer.data == response_content


@pytest.mark.django_db
def test_create_inventory(api_client1, service_setup, offer_inventory_setup):
    assert len(Item.objects.all()) == 1
    data = {
        "code": 'NEWW',
        "name": 'NEWW',
        "currency": service_setup['currency1'].id
    }
    response = api_client1['client'].post('/trading/item/', data, format='json')
    assert len(Item.objects.all()) == 2
    assert response.status_code == status.HTTP_201_CREATED
