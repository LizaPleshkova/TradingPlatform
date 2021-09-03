from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from trading.models import UserProfile, Trade, Offer
from trading.services import ProfitableTransactionsServices

User = get_user_model()


# for creating UserProfile after creating User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile = UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=Offer)
# def when_create_offer(sender, instance, created, **kwargs):
#     ''' search offers for trade'''
#     if created:
#         ProfitableTransactionsServices.requirements_for_transaction()
#         print('from signals when_create_offer')
#
