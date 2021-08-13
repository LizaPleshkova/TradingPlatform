from django.core.management.base import BaseCommand, CommandError
from trading.models import Offer, Item
from trading.enums import OfferCnoice


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('type_transaction', choices=[OfferCnoice.BUY.value, OfferCnoice.SELL.value])
        parser.add_argument('item-code', nargs='+', type=str, help='item-code')

    def handle(self, *args, **options):

        print(f'type_transaction: {options["type_transaction"]}')
        print(f'item-code: {options["item-code"]}')

        for item in options["item-code"]:
            print(item)
            if Item.objects.filter(code=item).exists():
                it = Item.objects.get(code=item)
                offers = Offer.objects.filter(type_transaction=options["type_transaction"], item=it)
                self.stdout.write(self.style.SUCCESS(offers))
            else:
                raise CommandError("item doesn't exist. try again")