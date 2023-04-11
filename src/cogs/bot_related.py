from datetime import datetime
from discord import Member, User, TextChannel, Embed, user
from discord.ext.commands import (
    Cog,
    command,
    cooldown,
    when_mentioned,
    BucketType,
)
from typing import Optional
from discord.ext.commands.core import Command, guild_only
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from src.data_clusters.configuration.server_vars import server


def syntax(command: Command):
    cmd_and_aliases = "|".join(
        sorted([str(command) for command in command.aliases])
    )
    params = list()

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(
                f"[{key}]" if "NoneType" in str(value) else f"<{key}>"
            )

    params = " ".join(params)

    return f"""`{command}|{cmd_and_aliases} {params}`"""


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        help_embed = Embed(
            title="Help",
            description=f"```{self.ctx.bot.PREFIX}command <argument>```",
            colour=self.ctx.author.colour,
        )
        help_embed.set_thumbnail(url=self.ctx.bot.user.avatar_url)
        help_embed.set_author(name="ProBotX")
        help_embed.set_footer(
            text=f"{offset:,} - {min(len_data,offset+self.per_page-1):,} of {len_data:,} commands."
        )

        for name, value in fields:
            help_embed.add_field(name=name, value=value, inline=False)
        return help_embed

    async def format_page(self, menu, entries):
        fields = list()
        for entry in entries:
            fields.append(
                (
                    f"{entry}",
                    f"{(entry.brief or 'No description')}\n{syntax(entry)}",
                )
            )
        return await self.write_page(menu, fields)


class BotRelated(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.remove_command("help")  # removing the standard 'help' cmd

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("bot_related")
        else:
            print("bot_related cog loaded")
        self.mod_chan = self.bot.get_channel(server.get("mod_chan"))

    # just like the *say fifi cmd, deletes og msg and sends another
    @command(
        name="echo",
        aliases=["say", "print"],
        brief="lets the bot send your message in a specified channel",
    )
    @guild_only()
    async def echo_msg(self, ctx, channel: Optional[TextChannel], *, msg):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(f"**You ain't no admin.**")
        channel = channel or ctx.channel
        if not msg:
            return await ctx.send("write a message.")

        await ctx.message.delete()
        await channel.send(msg)

        feedback_embed = Embed(
            title=f"Message sent to: #{str(channel)}",
            description=f"```{msg}```",
            colour=ctx.author.color,
        )
        feedback_embed.set_author(
            name=f"sender: {str(ctx.author)}",
            icon_url=f"{ctx.author.avatar_url}",
        )
        await self.mod_chan.send(embed=feedback_embed)

    @command(
        name="dm",
        aliases=["DM"],
        brief="DMs the specified user",
    )
    @cooldown(rate=3, per=300, type=BucketType.user)
    @guild_only()
    async def dm(
        self, ctx, user_mention: Optional[User], *, msg: Optional[str]
    ):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("**You ain't no admin.**")

        if not user_mention or not msg:
            return await ctx.send(
                f"`{self.bot.PREFIX}dm user_mention message`"
            )

        await ctx.message.delete()
        # await user_mention.send(f"{msg}\nSent by: **{ctx.author.name}**")

        dm_embed = Embed(
            title="Bot DM", colour=ctx.author.colour, timestamp=datetime.now()
        )
        dm_embed.set_footer(
            text=f"To: {user_mention.name}",
            icon_url=f"{user_mention.avatar_url}",
        )
        dm_embed.add_field(name="message content:", value=f"```{msg}```")

        await user_mention.send(embed=dm_embed)  # ? sending to user
        dm_embed.set_author(
            name=f"From: {ctx.author.name}",
            icon_url=f"{ctx.author.avatar_url}",
        )  # ? shows dm author
        await self.mod_chan.send(
            embed=dm_embed
        )  # ? sending log to mod channel

    @command(
        name="avatar",
        aliases=["av", "picture", "icon", "pic"],
        brief="sends the user's avatar",
    )
    @guild_only()
    async def fetch_av(self, ctx, *, av_member: Optional[Member] = None):
        if not av_member:
            av_url = ctx.author.avatar_url
        else:
            av_url = av_member.avatar_url
        await ctx.send(av_url)

    @guild_only()
    async def cmd_help(
        self, ctx, command
    ):  # func that creates and embed that has cmd in title, syntax of it in description and takes the command  as an arg
        cmd_help_embed = Embed(
            title=f"`{command}`", description=f"{syntax(command)}"
        )  # syntax of the cmd as defined in cogs

        cmd_help_embed.add_field(
            name="Command description", value=command.brief or "No description"
        )  # adds a field about a description of a command

        await ctx.send(embed=cmd_help_embed)  # sending the embed

    @command(
        name="help", brief="shows the commands, their usage and syntax"
    )  # the overridden help cmd
    @guild_only()
    async def show_help(
        self, ctx, cmd: Optional[str]
    ):  # m'help cmd_name, either u enter a command name of its None
        if not cmd:  # printing an embed including all cmds
            menu = MenuPages(
                source=HelpMenu(ctx, list(self.bot.commands)),
                clear_reactions_after=True,
                # delete_message_after=True,
                timeout=180,
            )
            await menu.start(ctx)
        else:
            if command := get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("Command doesn't exist!")


def setup(bot):
    bot.add_cog(BotRelated(bot))
