import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.lazy_django import skip_if_no_django
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import pytest
from rest_framework import status

from rest_framework.test import APIClient, APIRequestFactory
from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
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
@pytest.mark.django_db
def test_name_of_your_test(api_client):
    # Add your logic here
    # url = reverse('trading/currency')

    # client.login(username=username, password=password)
    # response = client.get('/myapi/api/')

    response = api_client.get('/trading/currency/')
    # response = CurrencyView.as_view({'get': 'list'})(request)
    print(response, response.data)
    assert response.status_code == status.HTTP_200_OK

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
