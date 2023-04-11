from datetime import datetime
from discord import Member
from discord.embeds import Embed
from discord.ext.commands import Cog, command
from typing import Optional

from discord.ext.commands.core import guild_only


class Info(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")
        else:
            print("info cog loaded")

    @command(
        name="userinfo",
        aliases=["ui", "user_info", "member_info", "mi", "memberinfo"],
        brief="info on server member",
    )
    @guild_only()
    async def user_info(self, ctx, member: Optional[Member]):
        if member:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(
                    f"You ain't no admin. Use `{self.bot.PREFIX}ui` only."
                )
        if not member:
            member = ctx.author
        # member = member or ctx.author
        try:
            is_booster = member.premium_since.strftime(r"%d-%b-%y")
        except:
            is_booster = "Not Boosting"
        try:
            member_activity = f"{str(member.activity.type).split('.')[-1].title()} {member.activity.name}"
        except:
            member_activity = "None"

        ui_embed = Embed(
            title=f"{str(member)} - User Info",
            colour=member.colour,
            timestamp=datetime.now(),
        )

        ui_embed.set_thumbnail(url=member.avatar_url)
        ui_embed.set_footer(
            text=f"request b {str(ctx.author)}", icon_url=ctx.author.avatar_url
        )

        fields = [
            ("User", f"{member.mention}", True),
            ("Avatar", f"[link]({member.avatar_url})", True),
            ("Is Bot?", member.bot, True),
            ("Status", str(member.status).title(), True),
            (
                "Activity",
                f"{member_activity}",
                True,
            ),
            (
                "Is Booster?",
                f"{is_booster}",
                True,
            ),
            ("Top Role", member.top_role.mention, True),
            (
                f"Roles [{len(member.roles)}]",
                f"{' '.join([f'{role.mention}' for role in member.roles[1:]])}",
                False,
            ),
            ("ID", member.id, False),
            (
                "Created:",
                member.created_at.strftime(r"%I:%M %p | %d-%b-%y"),
                True,
            ),
            (
                "Joined:",
                member.joined_at.strftime(r"%I:%M %p | %d-%b-%y"),
                True,
            ),
        ]

        for name, value, inline in fields:
            ui_embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=ui_embed)

    @command(
        name="serverinfo",
        aliases=["si", "server_info", "guild_info", "gi", "guildinfo"],
        brief="shows server info",
    )
    @guild_only()
    async def server_info(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(f"**You ain't no admin.**")
        si_embed = Embed(
            title=f"{ctx.guild.name} - Server info",
            colour=ctx.guild.owner.colour,
            timestamp=datetime.now(),
        )

        si_embed.set_thumbnail(url=ctx.guild.icon_url)
        si_embed.set_footer(
            text=f"request by {str(ctx.author)}",
            icon_url=ctx.author.avatar_url,
        )

        statuses = [
            len(
                list(
                    filter(
                        lambda m: str(m.status) == defined_status,
                        ctx.guild.members,
                    )
                )
            )
            for defined_status in ["online", "idle", "dnd", "offline"]
        ]

        fields = [
            ("Owner", ctx.guild.owner.mention, True),
            ("Region", str(ctx.guild.region).capitalize(), True),
            ("Members", len(ctx.guild.members), True),
            (
                "Humans",
                len(list(filter(lambda m: not m.bot, ctx.guild.members))),
                True,
            ),
            (
                "Bots",
                len(list(filter(lambda m: m.bot, ctx.guild.members))),
                True,
            ),
            ("Boosters", f"{ctx.guild.premium_subscription_count}", True),
            ("Banned", len(await ctx.guild.bans()), True),
            (
                "Statuses",
                f"🟢 {statuses[0]}  |  🟠 {statuses[1]}  |  🔴 {statuses[2]}  |  ⚪ {statuses[3]}",
                False,
            ),
            ("Text Chans", len(ctx.guild.text_channels), True),
            ("Voice Chans", len(ctx.guild.voice_channels), True),
            ("Categories", len(ctx.guild.categories), True),
            ("Roles", len(ctx.guild.roles), True),
            ("Invites", len(await ctx.guild.invites()), True),
            # ("\u200b", "\u200b", True),
            ("Emojis", len(ctx.guild.emojis), True),
            ("ID", ctx.guild.id, False),
            (
                "Created:",
                ctx.guild.created_at.strftime("%I:%M %p | %d-%b-%y"),
                False,
            ),
        ]

        for name, value, inline in fields:
            si_embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=si_embed)


def setup(bot):
    bot.add_cog(Info(bot))
