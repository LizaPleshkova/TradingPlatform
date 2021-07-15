from django.urls import path

from rest_framework import routers
from trading.views import OfferListUserView, ItemView, WatchListView, InventoryView

router = routers.SimpleRouter()

router.register(r'user-offers', OfferListUserView, basename='user-offers')
router.register(r'item', ItemView, basename='item')
router.register(r'watch-list', WatchListView, basename='watch-list')
router.register(r'inventory', InventoryView, basename='inventory')
# urlpatterns = [
#     path('hello/', HelloView.as_view(), name='hello'),
#     # path('all-offers/', views.OfferList.as_view(), name='all-offers'),
#     # path('user-offers/', views.OfferListUser.as_view(), name='user-offers'),
#     # path('offer/<int:id>/', views.OfferUserDetail.as_view(), name='user-offer'),
#
# ]
urlpatterns = router.urls
