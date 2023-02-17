from tortoise.models import Model
from tortoise.fields import IntField, BigIntField

from src import NotEnoughMoneyInBank


class Bank(Model):
    id = IntField(pk=True)
    stored_amount = BigIntField(default=0)

    @property
    def balance(self) -> int:
        return self.stored_amount

    async def add(self, amount: int):
        self.stored_amount += amount
        await self.save()

    async def withdraw(self, amount: int, force: bool = False):
        if amount > self.stored_amount and not force:
            raise NotEnoughMoneyInBank

        self.stored_amount -= amount
        await self.save()
