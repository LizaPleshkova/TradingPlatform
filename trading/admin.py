from django.contrib import admin

from django.contrib import admin
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory

admin.site.register(Currency)
admin.site.register(Item)
admin.site.register(Price)
admin.site.register(Offer)
admin.site.register(Trade)
admin.site.register(Inventory)
