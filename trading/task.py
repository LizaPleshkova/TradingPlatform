from celery import Celery, shared_task
from celery.schedules import crontab
from TradingPlatform.celery import app
from .services import TradeService, ProfitableTransactionsServices


#
# app = Celery('tasks', broker='pyamqp://guest@localhost//')


# @app.task
# def add(x, y):
#     return x + y
#
#
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # эта функция выполнится при запуске - настроим вызовы задачи test
#     sender.add_periodic_task(crontab(minute='*/2'), requirements_transaction, name='search-offers-for-trades')
#

# @app.task(name='TradingPlatform.trading.tasks.requirements_transaction')
@app.task(bind=True, name='TradingPlatform.trading.tasks.requirements_transaction')
def requirements_transaction():
    ProfitableTransactionsServices.requiremenets_for_transaction()
    # print(offers)
    # return offers
