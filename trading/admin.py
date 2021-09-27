from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from trading.enums import OfferCnoice
from trading.models import Currency, Item, Price, WatchList, Offer, Trade, Inventory, UserProfile


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name',)
    list_filter = ['code']
    search_fields = ['name']


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'currency')
    list_filter = ['code', 'currency']
    search_fields = ['code', 'name']


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'price')
    list_filter = ['date']
    search_fields = ['item']


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'

    def clean(self):
        """ checking quantity seller's stocks """
        try:
            if self.data.get('type_transaction') == OfferCnoice.SELL.value:
                inventory_seller = Inventory.objects.get(user=self.data.get('user'), item=self.data.get('item'))
                if inventory_seller.quantity <= int(self.data.get('quantity')):
                    raise forms.ValidationError('You want to sell more stocks than you have', code='invalid')
            if self.data.get('type_transaction') == OfferCnoice.BUY.value:
                user = User.objects.get(id=int(self.data.get('user')))
                buyer_profile = user.user_profile
                if int(buyer_profile.score) <= (float(self.data.get('quantity')) * float(self.data.get('price'))):
                    raise forms.ValidationError(
                        "There aren't enough cash in the account to buy such a quantity of dtocks", code='invalid'
                    )
        except Inventory.DoesNotExist:
            raise forms.ValidationError(
                "No Inventory seller matches the given query", code='invalid'
            )
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                'No UserProfile seller matches the given query', code='invalid'
            )


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_transaction', 'item', 'user', 'price', 'quantity', 'is_active',)
    list_filter = ['type_transaction', 'item', 'user', 'is_active']
    form = OfferForm


class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'buyer', 'seller_offer', 'buyer_offer', 'trade_date', 'price', 'quantity')
    list_filter = ['seller', 'buyer', 'trade_date']
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
