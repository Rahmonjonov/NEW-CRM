from django.db import models

from account.models import Company, Account
from account.functions import check_one_company_invoice
from paycom.exceptions import PaycomException


class Order(models.Model):
    ORDER_ON_WAIT = 1
    ORDER_IS_PAYED = 2
    ORDER_CANCELLED = -1

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    amount = models.BigIntegerField(blank=False)
    state = models.SmallIntegerField(blank=False)
    card = models.CharField(max_length=255, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def on_wait(self):
        return self.state == self.ORDER_ON_WAIT

    def is_payed(self):
        return self.state == self.ORDER_IS_PAYED

    def is_cancelled(self):
        return self.state == self.ORDER_CANCELLED

    def set_payed(self):
        self.state = self.ORDER_IS_PAYED
        self.add_company_balance()
        self.save()

    def cancel(self):
        self.state = self.ORDER_CANCELLED
        self.save()

    def add_company_balance(self):
        summa = self.amount / 100
        company = self.company
        company.balance += summa
        company.save()
        check_one_company_invoice(self.company)

    @staticmethod
    def find_by_pk(pk):
        try:
            order = Order.objects.get(pk=pk)
            return order
        except Order.DoesNotExist as e:
            raise PaycomException("ORDER_NOT_FOUND")
