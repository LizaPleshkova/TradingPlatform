from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    ''' currency - валюта '''
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'


class Item(models.Model):
    ''' particular stock - конкретная акция '''
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=255, unique=True)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    # price
    description = models.TextField("Details", blank=True, null=True, max_length=500)

    def __str__(self):
        return f'{self.name} - {self.currency.name}'


class Price(models.Model):
    ''' price - цена '''
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(unique=True, blank=True, null=True)


class WatchList(models.Model):
    ''' favorite list of stocks - избранное конкретного пользователя'''
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('user', 'item')

class Offer(models.Model):
    ''' заявка на продажу\покупку конкретной акции(item) '''
    BUY = 'BUY'
    SELL = 'SELL'
    OFFER_CHOICES = [
        (BUY, 'Buy stocks'),
        (SELL, 'Sell stocks')
    ]
    type_transaction = models.CharField(max_length=5, choices=OFFER_CHOICES, null=True)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    price = models.DecimalField("Requested price", max_digits=7,decimal_places=2,)
    quantity = models.IntegerField("Requested quantity")
    is_active = models.BooleanField(default=True)


class Trade(models.Model):
    ''' stock - сделка '''
    # item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    seller = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='seller_trade')
    buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='buyer_trade')
    # price = models.DecimalField("Requested price", max_digits=7)
    # quantity = models.IntegerField("Requested quantity")
    seller_offer = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='seller_trade')
    buyer_offer = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL, related_name='buyer_trade')
    description = models.TextField(max_length=500, blank=True, null=True,)

class Inventory(models.Model):
    '''  кол-во акций конкретного пользователя '''
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField("Quantity of stocks", default=0)
