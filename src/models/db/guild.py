from tortoise import fields
from tortoise.models import Model


class Guild(Model):
    id = fields.IntField(pk=True)
    discord_id = fields.IntField()

    def __int__(self):
        return self.discord_id

    def __str__(self):
        return f"[ Guild with id {self.discord_id} ] "

    def __repr__(self):
        return f'Guild({self.discord_id=}, {self.id=})'

