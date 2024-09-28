from enum import Enum


class OrderStatus(str, Enum):

    IN_PROGRESS = 'в процессе'
    PENDING = 'В процессе'
    PAID = 'Оплачен'
    CANCELED = "Отменен"