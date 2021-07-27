import json
import pytest
# from model_bakery import baker

from trading.serializers import OfferListSerializer, ItemSerializer, WatchListSerializer, \
    CurrencySerializer, PriceSerializer, TradeSerializer
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile, OfferCnoice
from trading.services import TradeService, OfferService, BaseService, ProfitableTransactionsServices
#
# class TestCurrencyEndpoints:
#
#     endpoint = '/api/currencies/'
#
#     def test_list(self, api_client, baker=None):
#         baker.make(Currency, _quantity=3)
#
#         response = api_client().get(
#             self.endpoint
#         )
#
#         assert response.status_code == 200
#         assert len(json.loads(response.content)) == 3
#
#
def test_updating_offer_is_active():
    pass