from src.data_clusters.configuration.server_vars import server
from discord import Intents, channel, Embed
from discord.activity import Game
from discord.enums import Status
from discord.ext.commands import Bot as BotBase, CommandNotFound
from discord.ext.commands.errors import (
    BadArgument,
    CommandOnCooldown,
    MissingRequiredArgument,
    NoPrivateMessage,
    MissingPermissions,
    BotMissingPermissions,
)
from discord.errors import HTTPException, Forbidden

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)  # for a better scheduler than discord's
from asyncio.tasks import sleep

from datetime import datetime
from glob import glob

# PREFIX = "m'"
PREFIX = server.get("prefix")
OWNER_ID = 747449468864954438
COGS = [
    path.split("/")[-1][:-3] for path in glob("./src/cogs/*.py")
]  # it returns a list of the cog names you're going to use, it uses the glob module to get the location of the cog files, then split the path and take the cog name and removing the .py extension.
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument)


class Ready(
    object
):  # making sure cogs are ready as bot methods are always executed b4 cog methods
    # this sets all attrs of cogs to false for when u load them
    def __init__(self) -> None:
        for cog in COGS:
            setattr(self, cog, False)

    # this sets the loaded cogs attrs to True when loaded
    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"    -{cog} cog ready")

    def all_ready(self):
        print("Cogs stuff started/finished")
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):  # inheriting from bot class
    def __init__(
        self,
    ):  # specifying the bots commands structure, prefix, help command, the bot's description,the options inside the command
        self.PREFIX = PREFIX
        # defines the guilds you want the bot to work on, setting it to None till I change it later, you define the servers you want the bot to work on or you make it automatically
        self.scheduler = AsyncIOScheduler()
        self.ready = False
        self.cogs_ready = Ready()
        self.TOKEN = server.get("token")

        # for db
        # db.autosave(self.scheduler)

        # TO SET CUSTOM INTENTS
        # intents = Intents.default()
        # intents.members = True

        super().__init__(
            command_prefix=PREFIX,
            OWNER_ID=OWNER_ID,
            intents=Intents.all(),  # get all the intents you want
            member=True,
        )

    # ? sets up the cogs for the bot
    def setup(self):
        for cog in COGS:
            self.load_extension(f"src.cogs.{cog}")

    def run(self, *args, **kwargs):
        self.setup()
        print("Running Bot...")
        super().run(self.TOKEN)

    async def on_connect(self):
        print("Bot Connected")

        game = Game(f"{self.PREFIX}")
        await self.change_presence(
            status=Status.idle, activity=game
        )  # ? Playin m'

    async def on_disconnect(self):
        print("Bot Disconnected, Reconnecting...")

    async def on_error(self, event_method, *args, **kwargs):
        if (
            event_method == "on_command_error"
        ):  # ?event_method is a str, on_command_error is when someone sends a wrong command
            await args[0].send(
                "Something went wrong"
            )  # ? args[0] is the channel where there's a wrong cmd
        raise

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            # ? isinstance gives true if the value is of the type
            # ? the error is if someone uses the prefix but the command is not found
            if isinstance(context.channel, channel.DMChannel):
                dm_help_embed = Embed(
                    title="DM Help",
                    description=f"For **Modmail**: use ```{self.PREFIX}modmail```\nFor **Confessions**: use ```{self.PREFIX}confess```",
                    colour=0x23272E,
                )
                return await context.send(embed=dm_help_embed)
            await context.send(
                f"**Command not found!**\nCheck `{self.PREFIX}help` for commands."
            )  # ? context is the channel, but it's not the best practice to send this on wrong command, try to get what the user was trying to type

        if any([isinstance(exception, err) for err in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exception, CommandOnCooldown):
            await context.send(
                f"**Command is on {str(exception.cooldown.type).split('.')[-1]} Cooldown!**\nWait for {exception.retry_after:,.1f}s.\n*Please stop spamming.*"
            )  # ? cooldown seconds are formatted to one floating point

        elif isinstance(exception, BadArgument):
            await context.send(f"**You wrote a wrong command!**")

        elif isinstance(exception, HTTPException):
            await context.send("**Can't send message**")
            raise exception

        elif isinstance(exception, Forbidden):
            await context.send("**Forbidden! I can't do that.**")

        elif isinstance(exception, MissingRequiredArgument):
            await context.send(
                "**There's an argument missing in the command you've sent!**"
            )
        elif isinstance(exception, NoPrivateMessage):
            dm_help_embed = Embed(
                title="DM Help",
                description=f"For **Modmail**: use ```{self.PREFIX}modmail```\nFor **Confessions**: use ```{self.PREFIX}confess```",
                colour=0x23272E,
            )
            await context.send(
                "**This command doesn't work on DMs!**", embed=dm_help_embed
            )
            # await context.send(embed=dm_help_embed)
        elif isinstance(exception, MissingPermissions):
            await context.send(f"**You don't have permission to do that!**")
        elif isinstance(exception, BotMissingPermissions):
            await context.send(
                f"**I don't have** `{' '.join(exception.missing_perms)}` **permissions.**"
            )

        elif hasattr(exception, "original"):
            raise exception  # a shorter exception, raise bygeblak 2el error fel shell
        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(server.get("server_id"))
            self.stdout = self.get_channel(server.get("ready_chan"))

            # betgeeb 2el channel id wet3ml assign
            self.scheduler.start()  # starting the scheduler for autosave() and such
            ready_txt = f"Bot Ready @ {(datetime.now()).strftime('%I:%M:%S %p | %d-%b-%y')}"

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print(ready_txt)

            # wait for the cogs to be ready as the bot methods are executed first

            # to send a msg to a channel
            # await self.stdout.send(ready_txt)  # method to send messages, asynchronous
            # await self.stdout.send(
            #     "https://www.youtube.com/watch?v=Dvut-96X-Ng&list=PLYeOw6sTSy6ZGyygcbta7GcpI8a5-Cooc&index=8&t=626s"
            # )
            # await self.stdout.send(
            #     file=File("D:\\niabc\Pictures\PFPs\\Kanye-West-MBDTF.jpg")
            # )
            # to send an embed to a channel
            testing_embed = Embed(
                title="ProBotX is now Online",
                description=f"Use `{self.PREFIX}help` for the commands",
                colour=0xED9D12,  # color of the stripe left to the embed
                timestamp=datetime.now(),  # example: Today at 3:50 PM
            )  # defining the base of the element

            # setting an author for the embed
            testing_embed.set_author(
                name="ProBotX",
                icon_url=r"https://i.imgur.com/rfKjvgl.png",
            )

            # setting a footer for the embed
            # testing_embed.set_footer(text="Footer for the embed *insert feet fetish joke here*")

            # setting an img & thumbnail
            # testing_embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/342232703195676674/a_f7614066541dcb8ddffca077d13dd5c6.gif?size=1024")
            # testing_embed.set_image(url="https://cdn.discordapp.com/attachments/870725388458946602/872479360962142248/unknown.png")

            # a good practice is to make a list of tuples and loop through them and add field by field
            # fields_to_add = [
            #     ("ofa7 1st", "1st val babyyyy", True),
            #     (
            #         "2nd field",
            #         "on the same line as the first 34an inline True (default value)",
            #         True,
            #     ),
            #     ("3rd one", "below 34an inline False", False),
            # ]

            # adding the fields to the embed.
            # to add more fields to the embed. you gotta add this line to define the field, law 2el embeds 3yzha gmb b3d 5ly 2el inline attr True (it's true by default), 8er keda htkon t7t b3d
            # for (
            #     name,
            #     val,
            #     inline_bln,
            # ) in fields_to_add:
            #     testing_embed.add_field(name=name, value=val, inline=inline_bln)

            # now sending the embed to the desired channel

            await self.stdout.send(embed=testing_embed)

        else:  # if the bot is already ready and u wanna restart it, it reconnects on it's own
            print("Bot Reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
