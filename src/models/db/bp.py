import config
from tortoise.models import Model
from tortoise import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from src.battlepass import BattlePassItemList

class BattlePassModel(Model):
    user_id = fields.IntField(unique=True)
    xp = fields.IntField(default=0)
    level = fields.IntField(default=0)
    premium = fields.BooleanField(default=False)

    class Meta:
        table = f"battlepass_{config.CURRENT_BP_SEASON}"

    async def get_user(self) -> 'User':
        from .user import User

        user, _ = await User.get_or_create(id=self.user_id)

        return user

    async def update_level(self) -> (bool, 'BattlePassItemList'):
        """
        :return: Returns True if level was changed, otherwise False
        """
        new_level = self.xp // config.BP_XP_PER_LEVEL

        if new_level != self.level:
            from src.battlepass import BattlePassEnum

            self.level = new_level
            await self.save()

            item_list = BattlePassEnum.get_by_level(self.level)
            user = await self.get_user()

            if item_list.paid and not self.premium:
                item_list = None
            else:
                await item_list.apply_all(user=user)

            return True, item_list

        return False, None

    async def add_xp(self, xp: int) -> None:
        self.xp += xp
        await self.save()

    @staticmethod
    def xp_to_level(xp: int) -> int:
        return xp // config.BP_XP_PER_LEVEL

    @staticmethod
    def level_to_xp(level: int) -> int:
        return level * config.BP_XP_PER_LEVEL