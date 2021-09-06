import stripe
from django.conf import settings
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
        instance.profile = UserProfile.objects.create(
            user=instance,
            stripe_client_id=stripe.Customer.create(
                email=instance.email,
                stripe_account=settings.STRIPE_ACCOUNT_ID,
                name=instance.username
            ).id
        )
