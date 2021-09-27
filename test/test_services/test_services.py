from decimal import Decimal
from django.contrib.auth import get_user_model
import pytest
from trading.models import Trade, Inventory, UserProfile
from trading.services.trade import (
    TradeService, ProfitableTransactionsService, _updating_offer_quantity, _updating_offer_is_active
)

User = get_user_model()


# for trade
@pytest.mark.django_db
def test_updating_price_item(offer_inventory_setup):
    ''' updating_price_item '''
    buyer_offer = offer_inventory_setup['offer1']
    price = buyer_offer.item.item_price.get().price
    assert price == Decimal('10.00')
    TradeService.updating_price_item(buyer_offer)
    price = buyer_offer.item.item_price.get().price
    assert price != Decimal('10.00')


@pytest.mark.django_db
def test_updating_offer_quantity(offer_inventory_setup):
    ''' _updating_offer_quantity '''
    buyer_offer = offer_inventory_setup['offer1']
    seller_offer = offer_inventory_setup['offer1']

    _updating_offer_quantity(buyer_offer, seller_offer)
    assert buyer_offer.quantity == buyer_offer.quantity - seller_offer.quantity


@pytest.mark.django_db
def test_updating_offer_is_active(offer_inventory_setup):
    ''' _updating_offer_quantity '''
    buyer_offer = offer_inventory_setup['offer1']

    assert buyer_offer.is_active == True
    _updating_offer_is_active(buyer_offer)
    assert buyer_offer.is_active == False


@pytest.mark.django_db
def test_updating_inventory_seller1(offer_inventory_setup):
    ''' updating_inventory_seller, when  buyer_offer.quantity > seller_offer.quantity '''
    buyer_offer = offer_inventory_setup['offer3']
    seller_offer = offer_inventory_setup['offer2']

    assert buyer_offer.quantity > seller_offer.quantity

    inv_sel = Inventory.objects.get(user=offer_inventory_setup['user1'])
    inv_buyer = Inventory.objects.get(user=offer_inventory_setup['user2'])
    assert inv_sel.quantity == 0
    assert inv_buyer.quantity == 0

    inv_after = TradeService.updating_inventory_seller(seller_offer, buyer_offer)

    assert inv_after.quantity == inv_sel.quantity - seller_offer.quantity


@pytest.mark.django_db
def test_updating_inventory_seller2(offer_inventory_setup):
    ''' updating_inventory_seller, when  buyer_offer.quantity <= seller_offer.quantity '''
    buyer_offer = offer_inventory_setup['offer1']
    seller_offer = offer_inventory_setup['offer2']

    assert buyer_offer.quantity <= seller_offer.quantity

    inv_before = Inventory.objects.get(user=offer_inventory_setup['user1'])
    assert inv_before.quantity == 0

    inv_after = TradeService.updating_inventory_seller(seller_offer, buyer_offer)

    assert inv_after.quantity == inv_before.quantity - buyer_offer.quantity


@pytest.mark.django_db
def test_updating_users_score1(offer_inventory_setup):
    ''' updating_users_score, when  buyer_offer.quantity > seller_offer.quantity '''
    buyer_offer = offer_inventory_setup['offer3']
    seller_offer = offer_inventory_setup['offer2']

    seller_profile = UserProfile.objects.get(user_id=seller_offer.user.id)
    buyer_profile = UserProfile.objects.get(user_id=buyer_offer.user.id)

    assert seller_profile.score == 0
    assert buyer_profile.score == 0

    buyer_profile_after, seller_profile_after = TradeService.updating_users_score(seller_offer, buyer_offer)

    assert buyer_profile_after.score == buyer_profile.score - seller_offer.quantity * buyer_offer.price
    assert seller_profile_after.score == seller_profile.score + seller_offer.quantity * buyer_offer.price


@pytest.mark.django_db
def test_updating_users_score2(offer_inventory_setup):
    ''' updating_users_score, when  buyer_offer.quantity <= seller_offer.quantity '''
    buyer_offer = offer_inventory_setup['offer1']
    seller_offer = offer_inventory_setup['offer2']

    seller_profile = UserProfile.objects.get(user_id=seller_offer.user.id)
    buyer_profile = UserProfile.objects.get(user_id=buyer_offer.user.id)

    assert seller_profile.score == 0
    assert buyer_profile.score == 0
    b_pr, s_pr = TradeService.updating_users_score(seller_offer, buyer_offer)

    assert b_pr.score == buyer_profile.score - buyer_offer.quantity * buyer_offer.price
    assert s_pr.score == seller_profile.score + buyer_offer.quantity * buyer_offer.price


@pytest.mark.django_db
def test_checking_offers_quantity(offer_inventory_setup):
    ''' checking_offers_quantity, that trade is creating'''
    buyer_offer = offer_inventory_setup['offer1']
    seller_offer = offer_inventory_setup['offer2']

    assert len(Trade.objects.all()) == 0

    trade = ProfitableTransactionsService.checking_offers_quantity(seller_offer, buyer_offer)

    assert len(Trade.objects.all()) == 1
