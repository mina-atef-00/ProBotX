from datetime import datetime
from typing import Optional, Union
from discord import Message
from discord.ext.commands.core import group, guild_only, has_permissions
from discord.member import Member
from src.data_clusters.configuration.server_vars import server
from discord import Embed
from discord import channel
from discord.ext.commands import Cog
from src.data_clusters.confessions.blocks import *


class Confessions(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("confessions")
            self.confessions_chan = self.bot.get_channel(
                server.get("confessions_chan")
            )
        else:
            print("confessions cog loaded")

    @group(
        invoke_without_command=True,
        brief="Post your confession to the server anonymously.",
    )
    async def confess(self, ctx, *, confession: Optional[str]):
        if not isinstance(ctx.channel, channel.DMChannel) and bool(confession):
            return await ctx.send(
                "**This command works only when DMing the bot.**"
            )
        elif not confession:
            # ? Sends Confessions Help Embed
            confess_help_embed = Embed(
                title="Confessions Help (DM the bot)",
                description=f"Send confession```{self.bot.PREFIX}confess <your_confession>```\nBlock member from confessing (admin)```{self.bot.PREFIX}confess block <member mention or id> or <confession_message_id>```\nUnblock a member (admin)```{self.bot.PREFIX}confess unblock <member mention or id>```\nBlocking commands can be done anywhere.",
                colour=0xFFFFFF,
            )
            return await ctx.send(embed=confess_help_embed)
        elif await check_id(ctx.author.id):
            return await ctx.send(
                "**You are blocked from sending confessions.**\n*I wonder why...*"
            )

        # ? sending embed to member
        to_mem_embed = Embed(
            title="Confession Sent!",
            description=f"Sent to {self.confessions_chan.mention}.\n**Confessions are anonymous, neither the moderators nor the Bot can know the user who sent the confession.**",
            colour=0xFFFFFF,
            timestamp=datetime.now(),
        )
        to_mem_embed.set_author(
            name=f"{str(self.bot.guild.name)}",
            icon_url=self.bot.guild.icon_url,
        )
        await ctx.message.add_reaction("👍")
        await ctx.send(embed=to_mem_embed)

        # ? sending embed to #confessions
        to_chan_embed = Embed(
            title="Member Confession",
            description=f'"{confession}"',
            colour=0xFFFFFF,
            timestamp=datetime.now(),
        )
        to_chan_embed.set_author(
            name=f"{str(self.bot.user.name)}",
            icon_url=self.bot.user.avatar_url,
        )
        to_chan_embed.set_thumbnail(url="https://i.imgur.com/qeRHkl6.jpg")
        await self.confessions_chan.send(embed=to_chan_embed)

        # ? adding confession and hashed member id to database
        confession_msg_id = self.confessions_chan.last_message_id
        add_confession_msg(member_id=ctx.author.id, msg_id=confession_msg_id)

    @has_permissions(administrator=True)
    @guild_only()
    @confess.command(name="block")
    async def confess_block(
        self, ctx, mem_msg_to_block: Union[Message, Member, None]
    ):
        if not mem_msg_to_block:
            return await ctx.send(
                "**You haven't added a member or a confession id.**"
            )

        if isinstance(mem_msg_to_block, Member):
            to_block = mem_msg_to_block.id

        elif isinstance(mem_msg_to_block, Message):
            msg_id = mem_msg_to_block.id
            if not await fetch_confession_sender_hash(msg_id):
                return await ctx.send("**This is not a confession message.**")
            to_block = await fetch_confession_sender_hash(msg_id)

        if not await block_id_hash(to_block):
            return await ctx.send("**User is already blocked.**")
        else:
            await ctx.message.add_reaction("🟩")
            await ctx.send("Member blocked, they can't confess now.")

    @has_permissions(administrator=True)
    @guild_only()
    @confess.command(name="unblock")
    async def confess_unblock(self, ctx, mem_to_unblock: Optional[Member]):
        if not mem_to_unblock:
            return await ctx.send("**You haven't added a member.**")

        if not unblock_id_hash(member_id=mem_to_unblock.id):
            return await ctx.send("**User is not blocked.**")
        else:
            await ctx.message.add_reaction("🟩")
            await ctx.send("Member unblocked, they can confess now.")
            await mem_to_unblock.send(
                "**You are now unblocked and you're able to confess.**"
            )


def setup(bot):
    bot.add_cog(Confessions(bot))
