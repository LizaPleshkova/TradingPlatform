import os
import sys
from celery import Celery
from celery._state import _set_current_app
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradingPlatform.settings')

app = Celery('TradingPlatform')
app.config_from_object('django.conf:settings', namespace='CELERY')
_set_current_app(app)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../TradingPlatform')))
django.setup()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.autodiscover_tasks()
app.conf.beat_schedule = {
    'search-offers-for-trades': {
        'task': 'TradingPlatform.trading.tasks.requirements_transaction',
        "schedule": 60.0,
    },
}
