from datetime import datetime, timedelta
from typing import Optional
from discord.ext.commands.converter import Greedy
from discord.ext.commands.core import guild_only
from src.data_clusters.configuration.server_vars import server
from discord import (
    Member,
    Embed,
)
from discord import Member, TextChannel
from discord.ext.commands import (
    Cog,
    command,
    CheckFailure,
    has_permissions,
    bot_has_permissions,
)


class ModChan(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mod_chan")
            self.mod_chan = self.bot.get_channel(server.get("mod_chan"))
            self.mute_role = self.bot.guild.get_role(
                server.get("role_on_mute")
            )

        else:
            print("mod_chan cog loaded")

    ########################################################################################################## #! PURGE
    @command(
        name="clear",
        aliases=["purge", "clr"],
        brief="clears messages in specified channel. you can delete up to 100 messages or messages from 14 days ago till in one go.",
    )
    @guild_only()
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(
        self,
        ctx,
        channel: Optional[TextChannel],
        members: Greedy[Member],
        limit: Optional[int] = 1,
    ):
        channel = channel or ctx.channel
        # print(f"{channel} {members} {limit}")

        def _check(
            message,
        ):  # ? checks whether u want to define messages from a member or all msgs, returns bool
            return not len(members) or message.author in members

        if 0 < limit <= 100:
            with channel.typing():  # ? typing status
                await ctx.message.delete()
                deleted = await channel.purge(
                    limit=limit,
                    after=datetime.now() - timedelta(days=14),
                    check=_check,
                )  # ? using the check func and making sure it's no more than 14 days, also deleting the purge command
                # ? message.delete returns a list of deleted messages
                await ctx.send(
                    f"**Deleted {len(deleted):,} messages.**", delete_after=5
                )
        else:
            await ctx.message.add_reaction("🟥")
            await ctx.send(
                "Your limit is 100 messages, minimum 1 message and up to 14 days before."
            )

    ########################################################################################################## #! MUTE
    @command(name="mute", brief="mutes a member(s)")
    @guild_only()
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def mute_members(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
        if not len(members):
            return await ctx.send(
                f"**You haven't provided members.**\nUse `{self.bot.PREFIX}mute member(s)_id reason(optional)` , make sure it's a user mention not a role mention."
            )
        else:
            for member in members:
                if not (
                    ctx.guild.me.top_role.position > member.top_role.position
                    or not ctx.author.top_role.position
                    > member.top_role.position
                ):
                    await ctx.send(
                        f"**{str(member)}'s top role is higher than mine/yours.**"
                    )
                    await ctx.message.add_reaction("🟥")
                    continue

                # ? ADD MUTE ROLE TO MEMBER
                try:
                    await member.edit(roles=[*member.roles, self.mute_role])
                    await ctx.message.add_reaction("🟩")
                except:
                    await ctx.send(
                        f"**Can't add the mute role to {member}.**\nMaybe the user is already muted or a wrong role_id."
                    )
                    await ctx.message.add_reaction("🟥")
                    continue
                # ? DM MEMBER
                try:
                    await member.send(
                        f"**You have been muted for:**\n```{reason}```**For a duration of:**\n```duration (wip)```"
                    )
                except:
                    pass

                mute_embed = Embed(
                    title="Member Muted",
                    colour=0x000000,
                    timestamp=datetime.now(),
                )
                mute_embed.set_author(
                    name=f"by: {str(ctx.author)}",
                    icon_url=ctx.author.avatar_url,
                )
                mute_embed.set_thumbnail(url=member.avatar_url)
                mute_embed.add_field(
                    name=f"{str(member)}",
                    value=f"**Reason:** ```{reason}```\n**For: `duration (wip)`**",
                    inline=True,
                )
                await self.mod_chan.send(embed=mute_embed)

    ########################################################################################################## #! UNMUTE
    @command(name="unmute", brief="unmutes a muted member(s)")
    @guild_only()
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def unmute_members(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
        if not len(members):
            return await ctx.send(
                f"****You haven't provided members.**\nUse `{self.bot.PREFIX}unmute member(s)_id reason(optional)` , make sure it's a user mention not a role mention."
            )
        else:
            for member in members:
                if not (
                    ctx.guild.me.top_role.position > member.top_role.position
                    or not ctx.author.top_role.position
                    > member.top_role.position
                ):
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**{str(member)}'s top role is higher than mine/yours.**"
                    )
                    continue

                # ? REMOVE MUTE ROLE FROM MEMBERS
                if not self.mute_role in member.roles:
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(f"**{str(member)} isn't muted.**")
                    continue

                await member.edit(
                    roles=list(set(member.roles) - set([self.mute_role]))
                )
                await ctx.message.add_reaction("🟩")

                # ? DM MEMBER
                try:
                    await member.send(
                        f"**You have been unmuted.**\n**Reason for unmute:**\n```{reason}```**For a duration of:**\n```duration (wip)```"
                    )
                except:
                    pass

                unmute_embed = Embed(
                    title="Member Unmuted",
                    colour=0xCECECE,
                    timestamp=datetime.now(),
                )
                unmute_embed.set_author(
                    name=f"by: {str(ctx.author)}",
                    icon_url=ctx.author.avatar_url,
                )
                unmute_embed.set_thumbnail(url=member.avatar_url)
                unmute_embed.add_field(
                    name=f"{str(member)}",
                    value=f"**Reason for unmute:** ```{reason}```\n**For: `duration (wip)`**",
                    inline=True,
                )
                await self.mod_chan.send(embed=unmute_embed)


def setup(bot):
    bot.add_cog(ModChan(bot))
