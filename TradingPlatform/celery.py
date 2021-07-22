import os
import crontab as crontab
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradingPlatform.settings')

app = Celery('TradingPlatform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# # celery beat tasks

# # app.conf.beat_schedule = {
# #     'send-spam-every-10-minute': {
# #         'tasks': 'main.tasks.send_beat_email',
# #         'schedule': crontab(minute='*/10')
# #     }
# # }
# #
# # user = User.objects.get(id=7)
# #
app.conf.beat_schedule = {

    'requirements-every-5-minuts': {
        # Регистрируем задачу. Для этого в качестве значения ключа task
        # Указываем полный путь до созданного нами ранее таска(функции)
        'task': 'TradingPlatform.tasks.requirements_transaction',

        # Периодичность с которой мы будем запускать нашу задачу
        # minute='*/5' - говорит о том, что задача должна выполнятся каждые 5 мин.
        'schedule': crontab(minute='*/1'),

        # Аргументы которые будет принимать функция
        # 'args': (*args)
    }
}
