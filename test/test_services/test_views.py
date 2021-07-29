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


#
# @pytest.mark.django_db
# def test_updating_offer_quantity(service_setup):
#     ''' test the create of user's profile after creation user'''
#     offer1 = Offer.objects.get(id=1)
#     assert offer1.is_active == True
#     _updating_offer_is_active(offer1)
#     assert offer1.is_active == False

#
# request = self.factory.get('test-user')
# force_authenticate(request, user=self.user1, token=self.user1_token)
#
# response = TestUserView.as_view()(request)
#
# question = Test.objects.filter(test__user=self.user1)
# serializer = MyTestListSerializer(question, many=True)
#
# self.assertEqual(response.status_code, 200)
# self.assertEqual(response.data, serializer.data)

# def test_jwt_auth():
#     resp = self.client.post(url, {'username': 'user@foo.com', 'password': 'pass'}, format='json')
#     self.assertEqual(resp.status_code, status.HTTP_200_OK)
#     self.assertTrue('token' in resp.data)
#     token = resp.data['token']
#     # print(token)
#

#  work

# @pytest.mark.django_db
# def test_get_currencies(api_client, service_setup):
#     response = api_client.get('/trading/currency/')
#     currencies = Currency.objects.all()
#     serializer = CurrencySerializer(currencies, many=True)
#     response_content = json.loads(response.content.decode('utf-8'))
#     assert serializer.data == response_content
#     assert response.status_code == status.HTTP_200_OK


# @pytest.mark.django_db
# def test_get_currency(api_client, service_setup):
#     currency1 = Currency.objects.get(id=1)
#     response = api_client.get('/trading/currency/{0}/'.format(currency1.id))
#     serializer = CurrencyDetailSerializer(currency1)
#     response_content = json.loads(response.content.decode('utf-8'))
#     assert serializer.data == response_content
#     assert response.status_code == status.HTTP_200_OK
#
# @pytest.mark.django_db
# def test_create_currency(api_client, service_setup):
#     response = api_client.post('/trading/currency/', {"code": "USD","name": "Usd"}, format='json')
#     currency1 = Currency.objects.all().last()
#
#     serializer = CurrencyDetailSerializer(currency1)
#     response_content = json.loads(response.content.decode('utf-8'))
#     print(response_content)
#     assert serializer.data == response_content
#     assert response.status_code == status.HTTP_201_CREATED
#
# @pytest.mark.django_db
# def test_create_currency(api_client, service_setup):
#     response = api_client.post('/trading/currency/', {"code": "USD","name": "Usd"}, format='json')
#     currency1 = Currency.objects.all().last()
#
#     serializer = CurrencyDetailSerializer(currency1)
#     response_content = json.loads(response.content.decode('utf-8'))
#     print(response_content)
#     assert serializer.data == response_content
#     assert response.status_code == status.HTTP_201_CREATED

# @pytest.mark.django_db
# def test_create_offer_valid(api_client, service_setup):
#     response = api_client.post('/trading/currency/', {"code": "USD","name": "Usd"}, format='json')
#     currency1 = Currency.objects.all().last()
#
#     serializer = CurrencyDetailSerializer(currency1)
#     response_content = json.loads(response.content.decode('utf-8'))
#     print(response_content)
#     assert serializer.data == response_content
#     assert response.status_code == status.HTTP_201_CREATED
#


# @pytest.mark.django_db
# def test_create_offer_valid(api_client1, service_setup):
#     ''' invalid, when sell and inventory_seller.quantity <= data.get('quantity')'''
#     profile = UserProfile.objects.get(id=1)
#     assert profile.score == 0
#
#     profile.score = 1000
#     profile.save(update_fields=["score"])
#
#     assert profile.score == 1000
#     data = {
#         "type_transaction": "BUY",
#         "item": 1,
#         "price": 5,
#         "quantity": 10
#     }
#     response = api_client1.post('/trading/user-offers/', data, format='json')
#
#     assert response.status_code == status.HTTP_201_CREATED
#
#
# @pytest.mark.django_db
# def test_create_offer_invalid(api_client2, service_setup):
#     ''' invalid, when inventory seller sell '''
#     inv = Inventory.objects.all()
#     assert len(inv) == 0
#
#     data = {
#         "type_transaction": "SELL",
#         "item": 1,
#         "price": 10,
#         "quantity": 10
#     }
#
#     response = api_client2.post('/trading/user-offers/', data, format='json')
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST





@pytest.mark.django_db
def test_serializer_offer_invalid(user_setup, service_setup, api_client2):
    ''' invalid, when buy and inventory_seller.quantity <= data.get('quantity')'''
    inv = Inventory.objects.all()
    assert len(inv) == 0

    data = {
        "user":user_setup.id,
        "type_transaction": "SELL",
        "item": 1,
        "price": 10,
        "quantity": 10
    }

    response = api_client2.post('/trading/user-offers/', data, format='json')

    # response = api_client.get('/trading/currency/')
    # response = CurrencyView.as_view({'get': 'list'})(request)
    print(response, response.data)
    assert response.status_code == status.HTTP_200_OK

    # assert response.status_code == status.HTTP_400_BAD_REQUEST
    # offer1 = Offer.objects.get(id=1)
    # response_content = json.loads(response.content.decode('utf-8'))
    # print(response_content)
    # assert response.status_code == status.HTTP_400_BAD_REQUEST

# @pytest.mark.django_db
# def test_create_offer_invalid(api_client, service_setup):
#     ''' invalid, when buy and inventory_seller.quantity <= data.get('quantity')'''
#     response = api_client.post('/trading/offer/', {
#         "type_transaction": "SELL",
#         "item": 1,
#         "price": 10,
#         "quantity": 10
#
#     }, format='json')
#     # offer1 = Offer.objects.get(id=1)
#     # response_content = json.loads(response.content.decode('utf-8'))
#     # print(response_content)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST

# @pytest.mark.django_db
# def test_valid_ser_offer(api_client, service_setup):
#     ''' invalid, when buy and inventory_seller.quantity <= data.get('quantity')'''
#     data = {
#         "type_transaction": "BUY",
#         "item": 1,
#         "price": 10,
#         "quantity": 10
#     }
#     profiles = UserProfile.objects.all()
#     assert len(profiles) == 0
#
#
#     with pytest.raises(ObjectDoesNotExist) as e:
#         ser = OfferDetailSerializer(data=data)
#         ser.is_valid(raise_exception=True)
#
# assert str(e.value) == 'No UserProfile seller matches the given query'

# @pytest.mark.django_db
# def test_name_of_your_test(api_fact):
#     # Add your logic here
#     # url = reverse('trading/currency')
#
#     # client.login(username=username, password=password)
#     # response = client.get('/myapi/api/')
#
#     request = api_client.get('/trading/currency')
#     response = CurrencyView.as_view({'get': 'list'})(request)
#     print(response)
#     assert response.status_code == status.HTTP_200_OK

# def test_details(rf, admin):
# request = rf.get('/customer/details')
# # Remember that when using RequestFactory, the request does not pass
# # through middleware. If your view expects fields such as request.user
# # to be set, you need to set them explicitly.
# # The following line sets request.user to an admin user.
# request.user = admin
# response = my_view(request)
# assert response.status_code == 200
