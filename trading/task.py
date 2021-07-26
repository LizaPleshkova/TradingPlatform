from .services import TradeService, ProfitableTransactionsServices
from celery import Celery, shared_task
from celery.schedules import crontab
from TradingPlatform.celery import app




#
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/1'), task_requirements_transaction, name='create trades')


@app.task(name='TradingPlatform.trading.tasks.requirements_transaction')
def task_requirements_transaction():
    ProfitableTransactionsServices.requiremenets_for_transaction()
