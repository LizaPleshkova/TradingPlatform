from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
import pytest
from rest_framework import serializers
from trading.serializers import OfferDetailSerializer
from trading.models import Inventory, UserProfile

User = get_user_model()


@pytest.mark.django_db
def test_signals(user1_setup):
    ''' test the create of user's profile after creation user'''
    user_profile1 = UserProfile.objects.all()
    assert len(user_profile1) == 1
    assert user_profile1.first().user == user1_setup


@pytest.mark.django_db
def test_serializer_offer_seller_invalid(user2_setup, service_setup):
    ''' invalid, when sell  and  seller's inventory DoesNotExist'''
    inv = Inventory.objects.all()
    assert len(inv) == 0

    data = {
        "user": user2_setup.id,
        "type_transaction": "SELL",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }

    with pytest.raises(ObjectDoesNotExist) as e:
        serializer = OfferDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == 'No Inventory seller matches the given query'


@pytest.mark.django_db
def test_serializer_offer_seller_invalid_quantity(user2_setup, service_setup, offer_inventory_setup):
    ''' invalid, when sell and inventory_seller.quantity <= data.get('quantity')'''
    inv = Inventory.objects.all().first()
    assert inv.quantity == 0

    data = {
        "user": user2_setup.id,
        "type_transaction": "SELL",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }

    with pytest.raises(serializers.ValidationError) as e:
        serializer = OfferDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_serializer_offer_seller_valid(user2_setup, service_setup, offer_inventory_setup):
    ''' invalid, when sell and inventory_seller.quantity <= data.get('quantity')'''
    inv = Inventory.objects.all()
    inventory = Inventory.objects.get(item=service_setup['item'], user=user2_setup)
    assert 2 == 2
    assert inventory.quantity == 0

    inventory.quantity = 50
    inventory.save(update_fields=["quantity"])

    assert inventory.quantity == 50

    data = {
        "user": user2_setup.id,
        "type_transaction": "SELL",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }

    serializer = OfferDetailSerializer(data=data)
    serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_serializer_offer_buyer_invalid_score(user1_setup, service_setup, offer_inventory_setup):
    ''' invalid, when buy and buyer_profile.score <= (data.get('quantity') * data.get('price'))'''
    profile = UserProfile.objects.get(user=user1_setup.id)
    assert profile.score == 0

    data = {
        "user": user1_setup.id,
        "type_transaction": "BUY",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }

    with pytest.raises(serializers.ValidationError) as e:
        serializer = OfferDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_serializer_offer_buyer_valid(user2_setup, service_setup):
    ''' invalid, when buy and buyer_profile.score <= (data.get('quantity') * data.get('price'))'''
    profile = UserProfile.objects.get(user=user2_setup.id)
    assert profile.score == 0

    profile.score = 1000
    profile.save(update_fields=["score"])

    assert profile.score == 1000

    data = {
        "user": user2_setup.id,
        "type_transaction": "BUY",
        "item": service_setup['item'].id,
        "price": 10,
        "quantity": 10
    }

    serializer = OfferDetailSerializer(data=data)
    serializer.is_valid(raise_exception=True)
