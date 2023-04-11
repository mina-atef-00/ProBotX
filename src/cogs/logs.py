from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog, check
from discord.member import Member
from discord.utils import get
from src.data_clusters.configuration.server_vars import server


class Logs(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("logs")
            self.msg_logs_channel = self.bot.get_channel(
                server.get("msg_logs_chan")
            )
            self.member_logs_channel = self.bot.get_channel(
                server.get("member_logs_chan")
            )
            self.server = self.bot.get_guild(server.get("server_id"))
            # print(self.server)
            # print(self.log_channel)

        else:
            print("logs cog loaded")

    @Cog.listener()
    async def on_user_update(self, before, after):
        # if before.guild != self.bot.guild:
        #     return
        if before.name != after.name:
            embed = Embed(
                title="Username change",
                description=f"{after.mention}",
                colour=after.colour,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{str(after)}", icon_url=f"{after.avatar_url}"
            )
            embed.set_footer(text=f"ID: {str(after.id)}")
            fields = [
                ("Before", before.name, True),
                (">After", after.name, True),
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.member_logs_channel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(
                title="Discriminator change",
                description=f"{after.mention}",
                colour=after.colour,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{str(after)}", icon_url=f"{after.avatar_url}"
            )
            embed.set_footer(text=f"ID: {str(after.id)}")
            fields = [
                ("Before", before.discriminator, True),
                (">After", after.discriminator, True),
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.member_logs_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(
                title="Avatar change",
                description=f"{after.mention}\nNew image is below, old is to the right.",
                colour=self.member_logs_channel.guild.get_member(
                    after.id
                ).colour,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{str(after)}", icon_url=f"{after.avatar_url}"
            )
            embed.set_footer(text=f"ID: {str(after.id)}")
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.member_logs_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if before.display_name != after.display_name:
            embed = Embed(
                title="Nickname change",
                description=f"{after.mention}",
                colour=after.colour,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{str(after)}", icon_url=f"{after.avatar_url}"
            )
            embed.set_footer(text=f"ID: {str(after.id)}")
            fields = [
                ("Before", before.display_name, True),
                (">After", after.display_name, True),
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.member_logs_channel.send(embed=embed)

        elif before.roles != after.roles:
            embed = Embed(
                title=f"Role {'added' if len(before.roles)<len(after.roles) else 'removed'}",
                colour=after.colour,
                timestamp=datetime.now(),
                description=f"**Role:** <@&{str((set(before.roles)^set(after.roles)))[10:28]}>\n**Top Role:** {after.top_role.mention}\n\nuser: {after.mention}",
            )
            embed.set_author(
                name=f"{str(after)}", icon_url=f"{after.avatar_url}"
            )
            embed.set_footer(text=f"ID: {str(after.id)}")
            fields = [
                (
                    "Before",
                    ", ".join([r.mention for r in before.roles]),
                    False,
                ),
                (">After", ", ".join([r.mention for r in after.roles]), False),
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.member_logs_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild != self.bot.guild:
            return

        if (not before.author.bot) and (
            not before.content.startswith(f"{self.bot.PREFIX}")
        ):
            if before.content != after.content:
                embed = Embed(
                    title=f"Message edit in #{after.channel}",
                    colour=after.author.colour,
                    timestamp=datetime.now(),
                )
                embed.set_author(
                    name=f"by: {str(after.author)}",
                    icon_url=f"{after.author.avatar_url}",
                )
                embed.set_footer(text=f"ID: {str(after.author.id)}")
                fields = [
                    ("Before", before.content, False),
                    (">After", after.content, False),
                ]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.msg_logs_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if message.guild != self.bot.guild:
            return

        if (not message.author.bot) and (
            not message.content.startswith(f"{self.bot.PREFIX}")
        ):
            embed = Embed(
                title=f"Message deletion in #{message.channel}",
                colour=message.author.colour,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"by: {str(message.author)}",
                icon_url=f"{message.author.avatar_url}",
            )
            embed.set_footer(text=f"ID: {str(message.author.id)}")
            fields = [("Message Content", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(
                    name=name, value=value or "nothing", inline=inline
                )

            await self.msg_logs_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
