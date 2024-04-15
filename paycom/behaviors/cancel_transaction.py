from .base import BaseBehavior
from paycom.models import Transaction
from orders.models import Order


class CancelTransaction(BaseBehavior):
    def execute(self):
        transaction = Transaction.find_by_pk(self.params['id'])
        if transaction.is_cancelled_after_payment():
            return transaction
        else:
            order = Order.find_by_pk(transaction.order_id)
            transaction.cancel(self.params['reason'])
            order.cancel()
            return transaction
