import discord as _discord


class DefaultEmbed(_discord.Embed):
    def __init__(self):
        super().__init__()

        self.colour = _discord.Colour.embed_background()
        self.set_footer(text="by gigalegit-#0880")
        self.timestamp = _discord.utils.utcnow()
