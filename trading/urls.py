from rest_framework import routers
from .views import (
    OfferListUserView, ItemView, WatchListView, InventoryView, PriceView, CurrencyView, ProfitableTransactions
)

router = routers.SimpleRouter()

router.register(r'user-offers', OfferListUserView, basename='user-offers')
router.register(r'item', ItemView, basename='item')
router.register(r'watch-list', WatchListView, basename='watch-list')
router.register(r'inventory', InventoryView, basename='inventory')
router.register(r'price', PriceView, basename='price')
router.register(r'currency', CurrencyView, basename='currency')

# profitable transaction
router.register(r'profitable-transactions', ProfitableTransactions, basename='profitable-transactions')

urlpatterns = router.urls
