import datetime
from tortoise.models import Model
from tortoise import fields


class XPBooster(Model):
    user_id = fields.IntField(unique=True)
    valid_until = fields.DatetimeField()
    power = fields.FloatField()

    @property
    def valid_until_no_tz(self) -> datetime.datetime:
        return self.valid_until.replace(tzinfo=None)

    async def apply(self):
        from src.models import User
        user = await User.get(id=self.user_id)
        user.xp_multiplier += self.power
        await user.save()

    async def unapply(self):
        from src.models import User
        user = await User.get(id=self.user_id)
        user.xp_multiplier -= self.power
        await user.save()

    @classmethod
    async def delete_all_expired(cls):
        for booster in await cls.all():
            if not booster.valid_until_no_tz < datetime.datetime.utcnow():
                return

            await booster.unapply()
            await booster.delete()
            await booster.save()
