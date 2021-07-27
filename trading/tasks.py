from .services import TradeService, ProfitableTransactionsServices
from TradingPlatform.celery import app
from celery.schedules import crontab


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # эта функция выполнится при запуске - настроим вызовы задачи test
    sender.add_periodic_task(crontab(minute='*/1'), requirements_transaction)


@app.task(name='TradingPlatform.trading.tasks.requirements_transaction')
def requirements_transaction():
    ProfitableTransactionsServices.requirements_for_transaction()