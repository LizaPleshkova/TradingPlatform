import os
from TradingPlatform.TradingPlatform.celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradingPlatform.settings')

app = Celery('TradingPlatform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# celery beat tasks

# app.conf.beat_schedule = {
#     'send-spam-every-10-minute': {
#         'tasks': 'main.tasks.send_beat_email',
#         'schedule': crontab(minute='*/10')
#     }
# }
