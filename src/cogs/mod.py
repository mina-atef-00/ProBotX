from discord.ext.commands.converter import Greedy
from discord.ext.commands.core import guild_only
from src.data_clusters.configuration.server_vars import server
from discord import (
    Member,
    Reaction,
    Embed,
    channel,
    colour,
    embeds,
    reaction,
    User,
    role,
    user,
)
from discord import Message, Member, Role
from discord.ext.commands import (
    Cog,
    bot,
    command,
    cooldown,
    when_mentioned,
    BucketType,
    CheckFailure,
    has_permissions,
    bot_has_permissions,
)
from discord.errors import HTTPException
from re import findall
from typing import Optional
from datetime import datetime


class Mod(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mod")
            self.mod_chan = self.bot.get_channel(server.get("mod_chan"))
            self.mute_role = self.bot.guild.get_role(
                server.get("role_on_mute")
            )

        else:
            print("mod cog loaded")

    ########################################################################################################## #! KICK
    # ? Greedy[type] takes multiple args of the type, keeps converting till can't then passes,just like defining *[members to ban] in the command
    @command(name="kick", brief="kicks a member(s)")
    @guild_only()
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
        if not len(members):
            return await ctx.send(
                f"**You haven't provided members.**\nUse `{self.bot.PREFIX}kick member(s)_id reason(optional)` , make sure it's a user mention not a role mention."
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

                try:
                    await member.kick(reason=reason)
                    await ctx.message.add_reaction("🟩")
                except:
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(f"**I can't kick {member}**")
                    continue

                kick_embed = Embed(
                    title="Member kicked",
                    colour=0xF47A07,
                    timestamp=datetime.now(),
                )
                kick_embed.set_author(
                    name=f"by: {str(ctx.author)}",
                    icon_url=ctx.author.avatar_url,
                )
                kick_embed.set_thumbnail(url=member.avatar_url)
                kick_embed.add_field(
                    name=f"{str(member)}",
                    value=f"**Reason:** ```{reason}```",
                    inline=True,
                )
                await self.mod_chan.send(embed=kick_embed)

    # ? check errrors
    # @kick_members.error
    # async def kick_members_error(self, ctx, exc):
    #     if isinstance(exc, CheckFailure):
    #         await ctx.send("You don't have permissions for that.")
    ########################################################################################################## #! BAN
    @command(name="ban", brief="bans a member(s)")
    @guild_only()
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def ban_members(
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "No reason provided.",
    ):
        if not len(members):
            await ctx.message.add_reaction("🟥")
            return await ctx.send(
                f"**You haven't provided members.**\nUse `{self.bot.PREFIX}ban member(s)_id reason(optional)` , make sure it's a user mention not a role mention."
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
                try:
                    await member.ban(reason=reason)
                    await ctx.message.add_reaction("🟩")
                except:
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(f"**I can't ban {member}**")
                    continue
                ban_embed = Embed(
                    title="Member banned",
                    colour=0xF40202,
                    timestamp=datetime.now(),
                )
                ban_embed.set_author(
                    name=f"by: {str(ctx.author)}",
                    icon_url=ctx.author.avatar_url,
                )
                ban_embed.set_thumbnail(url=member.avatar_url)
                ban_embed.add_field(
                    name=f"{str(member)}",
                    value=f"**Reason:** ```{reason}```",
                    inline=True,
                )
                await self.mod_chan.send(embed=ban_embed)

    ########################################################################################################## #! ADD ROLE
    @command(
        name="add_role",
        aliases=["addrole", "addroles", "add_roles", "add-roles", "add-role"],
        brief="adds a role(s) to member(s)",
        pass_context=True,
    )
    @guild_only()
    @has_permissions(administrator=True)
    async def add_role(
        self,
        ctx,
        members: Greedy[Member],
        roles: Greedy[Role],
    ):
        if (not len(members)) or (not len(roles)):
            return await ctx.send(
                f"**You haven't provided members or/and roles.**\nUse `{self.bot.PREFIX}add_role member(s)_id role(s)_id`"
            )
        else:
            for member in members:
                if (
                    not ctx.guild.me.top_role.position
                    > member.top_role.position
                    or not ctx.author.top_role.position
                    > member.top_role.position
                ):
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**{str(member)}'s top role is higher than mine/yours.**"
                    )
                    continue

                # ? ADD ROLES TO MEMBER
                try:
                    await member.edit(roles=[*member.roles, *list(roles)])
                    await ctx.message.add_reaction("🟩")
                except:
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**Can't add a role to {member}.**\nMaybe the user already has the role or there's a wrong role_id."
                    )
                    continue

    ########################################################################################################## #! REMOVE ROLE
    @command(
        name="remove_role",
        aliases=[
            "removerole",
            "removeroles",
            "remove_roles",
            "remove-roles",
            "remove-role",
            "remrole",
            "remroles",
            "rem_roles",
            "rem-roles",
            "rem-role",
        ],
        brief="removes a role(s) to member(s)",
        pass_context=True,
    )
    @guild_only()
    @has_permissions(administrator=True)
    async def remove_role(
        self,
        ctx,
        members: Greedy[Member],
        roles: Greedy[Role],
    ):
        if (not len(members)) or (not len(roles)):
            return await ctx.send(
                f"**You haven't provided members or/and roles.**\nUse `{self.bot.PREFIX}remove_role member(s)_id role(s)_id`"
            )
        else:
            for member in members:
                if (
                    not ctx.guild.me.top_role.position
                    > member.top_role.position
                    or not ctx.author.top_role.position
                    > member.top_role.position
                ):
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**{str(member)}'s top role is higher than mine/yours.**"
                    )
                    continue

                # ? REMOVE ROLES FROM MEMBER
                if not all(r in member.roles for r in list(roles)):
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**{str(member)} doesn't have all of the roles you defined.**"
                    )
                    continue

                try:
                    await member.edit(
                        roles=list(set(member.roles) - set(roles))
                    )
                    await ctx.message.add_reaction("🟩")
                except:
                    return await ctx.send(
                        "**Maybe you have provided a wrong role_id.**"
                    )

    ########################################################################################################## #! WARN
    @command(
        name="warn",
        brief="warns a member(s)",
    )
    @guild_only()
    @bot_has_permissions(administrator=True)
    @has_permissions(administrator=True)
    async def warn_member(  # TODO ADD A LOG FILE WARN, REMOVE WARN COMMAND, CLEAR WARNS COMMAND
        self,
        ctx,
        members: Greedy[Member],
        *,
        reason: Optional[str] = "no reason provided",
    ):
        if not len(members):
            return await ctx.send(
                f"**You haven't provided members.**\nUse `{self.bot.PREFIX}warn member(s)_id reason(optional)` , make sure it's a user mention not a role mention."
            )
        else:
            for member in members:
                if (
                    not ctx.guild.me.top_role.position
                    > member.top_role.position
                    or not ctx.author.top_role.position
                    > member.top_role.position
                ):
                    await ctx.message.add_reaction("🟥")
                    await ctx.send(
                        f"**{str(member)}'s top role is higher than mine/yours.**"
                    )
                    continue

                # ? DM MEMBER
                try:
                    await member.send(
                        f"**You have been warned for:**\n```{reason}```"
                    )
                except:
                    pass

                warn_embed = Embed(
                    title="Member Warned",
                    colour=0xFCED16,
                    timestamp=datetime.now(),
                )
                warn_embed.set_author(
                    name=f"by: {str(ctx.author)}",
                    icon_url=ctx.author.avatar_url,
                )
                warn_embed.set_thumbnail(url=member.avatar_url)
                warn_embed.add_field(
                    name=f"{str(member)}",
                    value=f"**Reason:** ```{reason}```",
                    inline=True,
                )
                await ctx.message.add_reaction("🟩")
                await self.mod_chan.send(embed=warn_embed)


def setup(bot):
    bot.add_cog(Mod(bot))
