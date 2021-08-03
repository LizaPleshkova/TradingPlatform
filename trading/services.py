from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from .models import Offer, Trade, Inventory, UserProfile, OfferCnoice


def _updating_offer_quantity(offer1, offer2):
    ''' offer1 > offer2 '''
    offer1.quantity = offer1.quantity - offer2.quantity
    offer1.save(update_fields=["quantity"])
    return offer1


def _updating_offer_is_active(offer):
    offer.is_active = False
    offer.save(update_fields=["is_active"])
    return offer


class ProfitableTransactionsServices:

    @staticmethod
    def requirements_for_transaction():
        buyer_offers = Offer.objects.filter(type_transaction=OfferCnoice.BUY.name,
                                            is_active=True)  # все офферы для покупки
        seller_offers = Offer.objects.filter(type_transaction=OfferCnoice.SELL.name,
                                             is_active=True)  # все офферы для продажи

        for buyer_offer in buyer_offers:
            for seller_offer in seller_offers:
                ProfitableTransactionsServices.checking_offers(buyer_offer, seller_offer)

    @staticmethod
    def checking_offers(buyer_offer, seller_offer):
        if buyer_offer.item == seller_offer.item:  # зафвки на одну и ту же items

            if buyer_offer.price <= seller_offer.price:
                ProfitableTransactionsServices.checking_offers_quantity(buyer_offer, seller_offer)

    @staticmethod
    def checking_offers_quantity(buyer_offer, seller_offer):
        if buyer_offer.quantity <= seller_offer.quantity:
            # купили столько акций, сколько было необходимо ( указано в заявке)

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)


            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks "
            )

            if buyer_offer.quantity - seller_offer.quantity == 0:
                _updating_offer_is_active(seller_offer)
            _updating_offer_quantity(seller_offer, buyer_offer)
            _updating_offer_is_active(buyer_offer)

        elif buyer_offer.quantity > seller_offer.quantity:
            # покупка акций по нескольким офферс

            TradeService.updating_users_score(seller_offer, buyer_offer)
            TradeService.updating_inventory_buyer(seller_offer, buyer_offer)
            TradeService.updating_inventory_seller(seller_offer, buyer_offer)
            TradeService.updating_price_item(buyer_offer)

            trade = Trade.objects.create(
                seller=seller_offer.user,
                buyer=buyer_offer.user,
                seller_offer=seller_offer,
                buyer_offer=buyer_offer,
                description=f"{buyer_offer.user} buy {seller_offer.user}'s stocks "
            )

            _updating_offer_quantity(buyer_offer, seller_offer)
            _updating_offer_is_active(seller_offer)
        return trade


class TradeService:

    @staticmethod
    def updating_inventory_buyer(seller_offer: Offer, buyer_offer: Offer):
        inventory_buyer, created = Inventory.objects.get_or_create(user=buyer_offer.user, item=buyer_offer.item)
        if buyer_offer.quantity > seller_offer.quantity:
            if created:
                inventory_buyer.quantity = seller_offer.quantity
            else:
                inventory_buyer.quantity += seller_offer.quantity
        elif buyer_offer.quantity <= seller_offer.quantity:
            if created:
                inventory_buyer.quantity = buyer_offer.quantity
            else:
                inventory_buyer.quantity += buyer_offer.quantity
        inventory_buyer.save(update_fields=["quantity"])

    @staticmethod
    def _get_sale_price_item(user_offer: Offer):
        ''' get price for sale '''
        price_item = user_offer.item.item_price.get()
        sale_price = price_item.price
        return sale_price

    @staticmethod
    def updating_users_score(seller_offer: Offer, buyer_offer: Offer):
        try:
            # ddeletet,hfnm
            seller_profile = UserProfile.objects.get(user_id=seller_offer.user.id)
            buyer_profile = UserProfile.objects.get(user_id=buyer_offer.user.id)

            if buyer_offer.quantity > seller_offer.quantity:
                buyer_profile.score = buyer_profile.score - seller_offer.quantity * buyer_offer.price
                seller_profile.score = seller_profile.score + seller_offer.quantity * buyer_offer.price
            elif buyer_offer.quantity <= seller_offer.quantity:
                buyer_profile.score = buyer_profile.score - buyer_offer.quantity * buyer_offer.price
                seller_profile.score = seller_profile.score + buyer_offer.quantity * buyer_offer.price
            buyer_profile.save(update_fields=["score"])
            seller_profile.save(update_fields=["score"])
            return buyer_profile, seller_profile
        except UserProfile.DoesNotExist:
            return "No UserProfile  matches the given query."

    @staticmethod
    def updating_inventory_seller(seller_offer: Offer, buyer_offer: Offer):
        '''updating_inventory_seller'''
        try:
            inventory_seller = Inventory.objects.get(user=seller_offer.user, item=seller_offer.item)
            if buyer_offer.quantity > seller_offer.quantity:
                inventory_seller.quantity -= seller_offer.quantity
            elif buyer_offer.quantity <= seller_offer.quantity:
                inventory_seller.quantity -= buyer_offer.quantity
            inventory_seller.save(update_fields=["quantity"])
            return inventory_seller
        except Inventory.DoesNotExist:
            raise ObjectDoesNotExist("No Inventory seller matches the given query.")

    @staticmethod
    def updating_price_item(buyer_offer: Offer):
        price_item = buyer_offer.item.item_price.get()
        price_item.price += Decimal(buyer_offer.price) * Decimal(0.05)
        price_item.save(update_fields=["price"])
