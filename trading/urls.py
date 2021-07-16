from django.urls import path

from rest_framework import routers
from trading.views import OfferListUserView, ItemView, WatchListView, InventoryView, \
    PriceView, CurrencyView, TradeView

router = routers.SimpleRouter()

router.register(r'user-offers', OfferListUserView, basename='user-offers')
router.register(r'item', ItemView, basename='item')
router.register(r'watch-list', WatchListView, basename='watch-list')
router.register(r'inventory', InventoryView, basename='inventory')
router.register(r'price', PriceView, basename='price')
router.register(r'currency', CurrencyView, basename='currency')
router.register(r'trade', TradeView, basename='trade')

urlpatterns = router.urls
