from datetime import datetime
from typing import Optional
from discord import Message
from discord.ext.commands.core import group
from discord.utils import get
from src.data_clusters.configuration.server_vars import server
from discord import Embed
from discord import channel
from discord.ext.commands import Cog


class ModMail(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mod_mail")
            self.mod_chan = self.bot.get_channel(server.get("mod_chan"))
            self.mod_mail_chan = self.bot.get_channel(
                server.get("mod_mail_chan")
            )
            self.mod_mail_categ = get(
                self.bot.guild.categories, id=server.get("mod_mail_categ")
            )

        else:
            print("mod_mail cog loaded")

    @Cog.listener()
    async def on_message(self, msg: Message):
        if not msg.author.bot:
            if not msg.content.startswith(self.bot.PREFIX):
                if isinstance(msg.channel, channel.DMChannel):
                    dm_help_embed = Embed(
                        title="DM Help",
                        description=f"**For Modmail:**```{self.bot.PREFIX}modmail open```\n**For Confessions:**```{self.bot.PREFIX}confess <your confession>```",
                        colour=0x23272E,
                    )
                    await msg.channel.send(embed=dm_help_embed)

    @group(
        invoke_without_command=True,
        brief="Send Mail to the server mods by DMing the bot.",
    )
    async def modmail(self, ctx):
        # ? Sends ModMail Help Embed
        modmail_help_embed = Embed(
            title="ModMail Help (DM the bot)",
            description=f"1- Open a ModMail ticket: ```{self.bot.PREFIX}modmail open```\n2- Send a message through ModMail: ```{self.bot.PREFIX}modmail send <your message>```\n3- Close a ModMail ticket: ```{self.bot.PREFIX}modmail close [reason]```",
            colour=0x23272E,
        )
        await ctx.send(embed=modmail_help_embed)

    @modmail.command(name="open")
    # ? Checks if there's a ticket channel already created using the topic
    async def modmail_open(self, ctx):
        if not isinstance(ctx.channel, channel.DMChannel):
            return await ctx.send("**This command works on DMs only**")

        if not bool(
            get(
                self.bot.guild.text_channels,
                topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
            )
        ):
            ###########################################
            # ? creates the ticket channel in the specified category with a special topic starting with member's id

            await self.bot.guild.create_text_channel(
                name=f"{ctx.author.name} {ctx.author.discriminator}",
                category=self.mod_mail_categ,
                topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
            )

            ################################
            # ? sends and embed showing some help to the user

            ticket_create_embed_user = Embed(
                title="Modmail Ticket Opened",
                description=f"To **send** a message to the mods: ```{self.bot.PREFIX}modmail send <your message>```\nTo **close** the ticket: ```{self.bot.PREFIX}modmail close <reason> (optional)```\n**Any other messages sent will be ignored**\n\n**Note:** `images don't get sent. You can send the picture on the dm normally, copy its link and then send it using the command, or send message links instead.`",
                colour=0x61AA79,
                timestamp=datetime.now(),
            )
            ticket_create_embed_user.set_author(
                name=f"Server: {str(self.bot.guild.name)}",
            )

            ticket_create_embed_user.set_footer(
                text=f"{str(ctx.author)} | {ctx.author.id}",
                icon_url=ctx.author.avatar_url,
            )
            ticket_create_embed_user.set_thumbnail(url=self.bot.guild.icon_url)
            await ctx.message.add_reaction("🟩")
            await ctx.send(embed=ticket_create_embed_user)

            ######################################
            # ? sends an embed to the modmail log channel

            ticket_create_embed_modmail_log = Embed(
                title="ModMail Ticket Opened",
                colour=0x61AA79,
                timestamp=datetime.now(),
            )

            ticket_create_embed_modmail_log.set_author(
                name=f"Server: {str(self.bot.guild.name)}",
                icon_url=self.bot.guild.icon_url,
            )
            ticket_create_embed_modmail_log.set_footer(
                text=f"{str(ctx.author)} | {ctx.author.id}",
                icon_url=ctx.author.avatar_url,
            )
            await self.mod_mail_chan.send(
                embed=ticket_create_embed_modmail_log
            )

            #################################
            # ? sends and embed to the ticket channel

            ticket_create_embed_ticket = Embed(
                title="ModMail Ticket Opened",
                description=f"To **send** a message to the user: ```{self.bot.PREFIX}modmail send <your message>```\nTo **close** the ticket: ```{self.bot.PREFIX}modmail close <reason> (optional)```\n**- Any other messages sent will be ignored**\n\n**- Your name won't be shown when sending the user a message.**\n**Note:** `images don't get sent. You can send the picture on the dm normally, copy its link and then send it using the command, or send message links instead.`",
                colour=0x61AA79,
                timestamp=datetime.now(),
            )
            ticket_create_embed_ticket.add_field(
                name="User", value=f"{ctx.author.mention}", inline=True
            )
            ticket_member = get(self.bot.guild.members, id=ctx.author.id)
            ticket_create_embed_ticket.add_field(
                name=f"Roles [{len(ticket_member.roles)}]",
                value=f"{' '.join([f'{role.mention}' for role in ticket_member.roles[1:]])}",
                inline=False,
            )
            ticket_create_embed_ticket.set_footer(
                text=f"{str(ctx.author)} | {ctx.author.id}",
                icon_url=ctx.author.avatar_url,
            )
            ticket_create_embed_ticket.set_thumbnail(url=ctx.author.avatar_url)
            ticket_chan = get(
                self.bot.guild.text_channels,
                topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
            )
            await ticket_chan.send(embed=ticket_create_embed_ticket)

        ##################################
        # ? sends error to the member when there's a ticket channel already there

        else:
            await ctx.message.add_reaction("🟥")
            return await ctx.send(
                f"**There's ModMail ticket already opened!**\nUse `{self.bot.PREFIX}modmail close` to close the existing ticket."
            )

    @modmail.command(name="send")
    async def modmail_send(self, ctx, *, msg):
        if isinstance(ctx.channel, channel.DMChannel) and bool(
            get(
                self.bot.guild.text_channels,
                topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
            )
        ):
            mem_to_mod_embed = Embed(
                title="Member Message",
                description=f"{msg}",
                colour=0x4399EF,
                timestamp=datetime.now(),
            )
            mem_to_mod_embed.set_author(
                name=f"to: {str(self.bot.guild.name)}",
                icon_url=self.bot.guild.icon_url,
            )
            mem_to_mod_embed.set_footer(
                text=f"from: {str(ctx.author)} | {ctx.author.id}",
                icon_url=ctx.message.author.avatar_url,
            )

            await get(
                self.bot.guild.text_channels,
                topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
            ).send(embed=mem_to_mod_embed)
            await ctx.send(embed=mem_to_mod_embed)

        elif (
            not isinstance(ctx.channel, channel.DMChannel)
            and "#ModMail-1,2,3#" in ctx.channel.topic
            and ctx.author.top_role.permissions.administrator
        ):
            receiving_member = get(
                self.bot.guild.members, id=int(ctx.channel.topic[:18])
            )
            mod_to_mem_embed = Embed(
                title="Mod Message",
                description=f"{msg}",
                colour=0xE5C07B,
                timestamp=datetime.now(),
            )
            mod_to_mem_embed.set_author(
                name=f"from: {str(self.bot.guild.name)}",
                icon_url=self.bot.guild.icon_url,
            )
            mod_to_mem_embed.set_footer(
                text=f"to: {str(receiving_member)} | {receiving_member.id}",
                icon_url=receiving_member.avatar_url,
            )

            await ctx.message.delete()
            await receiving_member.send(embed=mod_to_mem_embed)

            mod_to_mem_embed.set_author(
                name=f"{str(ctx.author)} (HIDDEN FROM MEMBER)",
                icon_url=ctx.author.avatar_url,
            )
            await ctx.send(embed=mod_to_mem_embed)

        else:
            return await ctx.send(
                f"**You don't have a ticket opened!**\nDM me using `{self.bot.PREFIX}modmail open` to open a ticket"
            )

    @modmail.command(name="close")
    async def modmail_close(
        self, ctx, reason: Optional[str] = "no reason provided."
    ):
        if not (
            (
                isinstance(ctx.channel, channel.DMChannel)
                and bool(
                    get(
                        self.bot.guild.text_channels,
                        topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
                    )
                )
            )
            or (
                (
                    "#ModMail-1,2,3#" in ctx.channel.topic
                    and ctx.author.top_role.permissions.administrator
                )
            )
        ):
            return await ctx.send(
                f"**You don't have a ticket opened here!**\nUse `{self.bot.PREFIX}modmail`"
            )
        else:
            # ? defining the modmail member and the ticket channel on server
            if isinstance(ctx.channel, channel.DMChannel):
                ticket_chan = get(
                    self.bot.guild.text_channels,
                    topic=f"{ctx.author.id} - {self.bot.guild.id} | Please don't change anything. #ModMail-1,2,3#",
                )
            else:
                ticket_chan = ctx.channel

            receiving_member = get(
                self.bot.guild.members, id=int(ticket_chan.topic[:18])
            )
            ##########################################################
            # ? deleting the ticket channel
            await ticket_chan.delete()
            ##########################################################
            # ? the embed getting sent to the user, shows that either him or an anon mod closed it and for an optional reason
            ticket_delete_embed_user = Embed(
                title="Modmail Ticket Closed",
                description=f"**Reason:** {reason}\n**By:** {str(ctx.author) if isinstance(ctx.channel,channel.DMChannel) else 'Mod'}",  # ? By Member name if command invoked in dm_channel else it's Mod
                colour=0xEF7B72,
                timestamp=datetime.now(),
            )
            ticket_delete_embed_user.set_author(
                name=f"Server: {str(self.bot.guild.name)}",
                icon_url=self.bot.guild.icon_url,
            )
            ticket_delete_embed_user.set_footer(
                text=f"{str(receiving_member)} | {receiving_member.id}",
                icon_url=receiving_member.avatar_url,
            )
            await receiving_member.send(
                embed=ticket_delete_embed_user
            )  # ? sending the embed to the member in DMs

            #####################################################################
            # ? the embed getting sent to the logs, shows that either him or a mod closed it and for an optional reason
            ticket_delete_embed_logs = Embed(
                title="Modmail Ticket Closed",
                description=f"**Reason:** {reason}\n**By:** {str(ctx.author)}",  # ? Must show name
                colour=0xEF7B72,
                timestamp=datetime.now(),
            )
            ticket_delete_embed_logs.set_author(
                name=f"Server: {str(self.bot.guild.name)}",
                icon_url=self.bot.guild.icon_url,
            )
            ticket_delete_embed_logs.set_footer(
                text=f"{str(receiving_member)} | {receiving_member.id}",
                icon_url=receiving_member.avatar_url,
            )
            await self.mod_mail_chan.send(
                embed=ticket_delete_embed_logs
            )  # ? sending the embed to the modmail logs channel


def setup(bot):
    bot.add_cog(ModMail(bot))
