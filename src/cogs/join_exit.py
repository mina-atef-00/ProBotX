from datetime import datetime
from discord import Member, Embed, Forbidden
from discord.ext.commands import Cog
from src.data_clusters.configuration.server_vars import server


class JoinExit(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("join_exit")
        else:
            print("join_exit cog loaded")
        self.join_exit_chan = self.bot.get_channel(
            server.get("join_exit_chan")
        )
        self.mod_chan = self.bot.get_channel(server.get("mod_chan"))
        self.newbie_chan = self.bot.get_channel(server.get("newbie_chan"))

    @Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild != self.bot.guild:
            return

        member_welcome_embed = Embed(
            title="Member Joined",
            description=f"Welcome {member.mention} to **{member.guild}**!\nHead to {'roles channel'} to get yo self some roles Bestie.",
            colour=member.colour,
            timestamp=datetime.now(),
        )
        member_welcome_embed.set_thumbnail(url=member.avatar_url)
        member_welcome_embed.set_image(
            url="https://media3.giphy.com/media/hVEBWRInEvNOEVS18i/giphy.gif"
        )
        if self.newbie_chan:
            self.newbie_chan = self.bot.get_channel(server.get("newbie_chan"))
        try:
            await member.send(embed=member_welcome_embed)
        except Forbidden:
            return print("Forbidden")
        except:
            pass
        await self.newbie_chan.send(embed=member_welcome_embed)

        ###############################################
        # ? JOIN LOG
        join_log_embed = Embed(
            title="Member Joined",
            description=f"{member.mention}",
            colour=member.colour,
            timestamp=datetime.now(),
        )
        join_log_embed.set_author(
            name=f"{str(member)}", icon_url=f"{member.avatar_url}"
        )
        join_log_embed.add_field(
            name="Created:",
            value=member.created_at.strftime("%I:%M %p | %d-%b-%y"),
            inline=True,
        )
        join_log_embed.set_footer(text=f"ID: {str(member.id)}")

        await self.join_exit_chan.send(embed=join_log_embed)
        ##############################################
        # ? ADD ROLES TO MEMBER
        join_role = member.guild.get_role(server.get("role_on_join_id"))
        try:
            await member.edit(roles=[*member.roles, join_role])
            # func overwrites roles so we add list of *list of existing plus new role, to add multiple: make a list of em and make [roles=[*member.roles, *join_roles_list]]
        except:
            await self.mod_chan.send(
                f"Can't add a join role.\n Either a wrong role_id or it's higher than my role."
            )

    @Cog.listener()
    async def on_member_remove(
        self, member: Member
    ):  # works on leaving server, deleting account
        if member.guild != self.bot.guild:
            return

        # ? SENDS TO USER ON LEAVING
        member_leave_embed = Embed(
            title="Member Left",
            description=f"WHY DID YOU LEAVE ME?!\n{member.mention}",
            colour=member.colour,
            timestamp=datetime.now(),
        )
        member_leave_embed.set_thumbnail(url=member.avatar_url)
        member_leave_embed.set_image(url="https://i.imgur.com/ekUSuhu.png")

        ##############################################
        # ? LEAVE LOG
        leave_log_embed = Embed(
            title="Member Left",
            description=f"{member.mention}",
            colour=member.colour,
            timestamp=datetime.now(),
        )
        leave_log_embed.set_author(
            name=f"{str(member)}", icon_url=f"{member.avatar_url}"
        )
        leave_log_embed.add_field(
            name="Joined:",
            value=member.joined_at.strftime("%I:%M %p | %d-%b-%y"),
            inline=True,
        )
        leave_log_embed.add_field(
            name="Top Role", value=member.top_role.mention, inline=False
        )

        leave_log_embed.add_field(
            name=f"Roles [{len(member.roles)}]",
            value=" ".join(r.mention for r in member.roles),
            inline=False,
        ),
        leave_log_embed.set_footer(text=f"ID: {str(member.id)}")

        await self.join_exit_chan.send(embed=leave_log_embed)
        #######################################
        try:
            await member.send(embed=member_leave_embed)
        except Forbidden:
            return print("Forbidden")
        except:
            pass


def setup(bot):
    bot.add_cog(JoinExit(bot))
