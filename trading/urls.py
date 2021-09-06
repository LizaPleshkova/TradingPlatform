from os import path

from rest_framework import routers

from . import views
from .views import (
    OfferListUserView, ItemView, WatchListView, InventoryView, PriceView, CurrencyView, ProfitableTransactions,
    StatisticViews, PaymentView,

)

router = routers.SimpleRouter()

router.register(r'user-offers', OfferListUserView, basename='user-offers')
router.register(r'item', ItemView, basename='item')
router.register(r'watch-list', WatchListView, basename='watch-list')
router.register(r'inventory', InventoryView, basename='inventory')
router.register(r'price', PriceView, basename='price')
router.register(r'currency', CurrencyView, basename='currency')
router.register(r'statistic', StatisticViews, basename='statistic')
router.register(r'payment', PaymentView, basename='payment')

# profitable transaction
router.register(r'profitable-transactions', ProfitableTransactions, basename='profitable-transactions')
#
urlpatterns = router.urls

