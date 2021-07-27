from django.contrib import admin
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name',)
    list_display = ('code', 'name')
    list_filter = ['code']
    search_fields = ['name']


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name',)
    list_filter = ['code']
    search_fields = ['code', 'name']


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'price')
    list_filter = ['date']
    search_fields = ['item']


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_transaction', 'item', 'user' , 'is_active',)
    list_filter = ['type_transaction', 'item', 'user', 'is_active']
    # search_fields = ['']


class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'buyer', 'seller_offer', 'buyer_offer')
    list_filter = ['seller', 'buyer']
    search_fields = ['seller', 'buyer']


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'quantity')
    list_filter = ['user']
    search_fields = ['user', 'item']


class WatchListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item',)
    list_filter = ['user']
    search_fields = ['user', 'item']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_filter = ['user']
    search_fields = ['user']


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
