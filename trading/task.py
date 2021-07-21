from celery import Celery
from .services import TradeService

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def add(x, y):
    return x + y


@app.task
def requirements_transaction(user):
    # нужно передавать user (который авторизован)
    print(user)
    offers = TradeService.requiremenets_for_transaction(user)
    print(offers)
    return offers
