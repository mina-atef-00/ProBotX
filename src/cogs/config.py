from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands.core import group, guild_only, has_permissions
from src.data_clusters.configuration.server_vars import server


class Config(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("config")
            self.mod_chan = self.bot.get_channel(server.get("mod_chan"))
        else:
            print("config cog loaded")

    @has_permissions(administrator=True)
    @group(
        name="config",
        aliases=["conf", "setup", "settings", "preferences", "prefs"],
        brief="Configure Bot Preferences",
        invoke_without_command=True,
    )
    @guild_only()
    async def config(self, ctx):
        config_embed = Embed(
            colour=self.bot.user.colour,
            title="Bot Configuration",
            timestamp=datetime.now(),
            description=f"**To Change a Setting:**```{self.bot.PREFIX}config set [setting name] [value or off]```\n-----------------\n**Settings Variables:**",
        )
        config_embed.set_thumbnail(
            url=r"https://upload.wikimedia.org/wikipedia/commons/e/ea/Settings_%28iOS%29.png"
        )
        fields = list()
        # print(list(server.keys())[4:])
        for setting_name in list(server.keys())[4:]:
            # print(setting_name)
            fields.append(
                (
                    f"+ {setting_name}",
                    f"- {server[f'{setting_name}']['brief']}\n- value: `{server[f'{setting_name}']['value']}`\n",
                    False,
                )
            )

        for name, val, inline in fields:
            config_embed.add_field(name=name, value=val, inline=inline)

        return await ctx.send(embed=config_embed)


def setup(bot):
    bot.add_cog(Config(bot))
