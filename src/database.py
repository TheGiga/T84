from tortoise import Tortoise


async def db_init():
    await Tortoise.init(
        db_url='sqlite://bot.db',
        modules={'models': ['src.models.db']}
    )

    print('Database initialised...')

    await Tortoise.generate_schemas(safe=True)
