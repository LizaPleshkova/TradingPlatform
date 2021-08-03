from enum import Enum


class OfferCnoice(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
