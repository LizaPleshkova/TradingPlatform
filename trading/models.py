from enum import Enum

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ''' userprofile with user's score'''
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    score = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, default=0)

    def __str__(self):
        return f'{self.id} - {self.user.username} - {self.score}'


class Currency(models.Model):
    ''' currency '''
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.id} - {self.code} - {self.name}'

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'


class Item(models.Model):
    ''' particular stock '''
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=255, unique=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='currency_item')
    description = models.TextField("Details", blank=True, null=True, max_length=500)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Price(models.Model):
    ''' price stock'''
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL, related_name='item_price')
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL,
                                 related_name='currency_price')
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(unique=True, blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.item} - {self.price}'


class WatchList(models.Model):
    ''' favorite list of stocks '''
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_watchlist')
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL, related_name='item_watchlist')

    def __str__(self):
        return f'{self.user.username} - {self.item}'

    class Meta:
        unique_together = ('user', 'item')


class OfferCnoice(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Offer(models.Model):
    ''' request for buy\sell a specific stock '''

    type_transaction = models.CharField("Type of transaction", max_length=5, choices=OfferCnoice.choices(), null=True)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL, related_name='item_offer')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_offer')
    price = models.DecimalField("Requested price", max_digits=7, decimal_places=2, )
    quantity = models.IntegerField("Requested quantity")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id} - {self.type_transaction} - {self.item} - {self.user.username}'


class Trade(models.Model):
    ''' trade '''
    seller = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='seller_trade')
    buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='buyer_trade')

    seller_offer = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='seller_trade')
    buyer_offer = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL, related_name='buyer_trade')
    description = models.TextField(max_length=500, blank=True, null=True, )

    def __str__(self):
        return f'{self.id} - {self.description}'


class Inventory(models.Model):
    '''  user's quantity stocks  '''
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_inventory')
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL, related_name='item_inventory')
    quantity = models.IntegerField("Quantity of stocks", default=0)

    def __str__(self):
        return f'{self.id} - {self.user.username} - {self.item} - {self.quantity}'
