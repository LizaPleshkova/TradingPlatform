from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from trading.models import Offer, Item, Trade
from trading.enums import OfferCnoice


class Command(BaseCommand):

    def handle(self, *args, **options):
        trades = Trade.objects.all()
        for trade in trades:
            trade.trade_date = datetime.now()
        Trade.objects.bulk_update(trades, ['trade_date'])
