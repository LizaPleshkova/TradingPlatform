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
from trading.services import TradeService, OfferService, BaseService, ProfitableTransactionsServices, \
    _updating_offer_quantity, _updating_offer_is_active

User = get_user_model()
#
#
# # class TestCurrencyEndpoints:
# #
# #     endpoint = '/api/currencies/'
# #
# #     def test_list(self, api_client, baker=None):
# #         baker.make(Currency, _quantity=3)
# #
# #         response = api_client().get(
# #             self.endpoint
# #         )
# #
# #         assert response.status_code == 200
# #         assert len(json.loads(response.content)) == 3
# #
#
# @pytest.mark.django_db
# def test_updating_offer_is_active(service_setup):
#     user1 = User.objects.get(id=1)
#     assert user1
#
#
# @pytest.mark.django_db
# def test_signals(signals_setup):
#     ''' test the create of user's profile after creation user'''
#     user_profile1 = UserProfile.objects.all()
#     assert len(user_profile1) == 1
#     assert user_profile1.first().user == signals_setup
#
#
# @pytest.mark.django_db
# def test_updating_offer_is_active(service_setup):
#     ''' test the create of user's profile after creation user'''
#     offer1 = Offer.objects.get(id=1)
#     assert offer1.is_active == True
#     _updating_offer_is_active(offer1)
#     assert offer1.is_active == False
#
#
