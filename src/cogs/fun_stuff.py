# implicit imports are cleaner and faster to import, rather than discord.ext.commands.command
from discord.ext.commands.core import guild_only
from src.data_clusters.configuration.server_vars import server
from discord import Member, Embed, channel
from discord.ext.commands import Cog, command, cooldown, BucketType
from discord.message import Message
from discord.ext.commands.errors import BadArgument
from re import findall
from typing import Optional
from random import choice, randint
from aiohttp import request
from datetime import datetime


class FunStuff(Cog):
    def __init__(self, bot) -> None:  # specified bot as argument
        self.bot = bot

    @command(
        name="greet-bot",
        hidden=False,
        pass_context=False,
        brief="greets you",
    )  # hidden attr doesn't show command in help command
    async def say_hello(self, ctx):
        await ctx.send(
            f"{choice(('Greetings','Welcome','My salutations','I welcome you'))}{ctx.author.mention}..."
        )  # replies to the sender of the command
        # f"Hello {ctx.author.mention}!"

    @command(name="dice", aliases=["roll"], brief="roll a dice")
    # @cooldown(rate=1, per=60, type=BucketType.user)  # cooldown for commands, 1 time per 60s
    # cooldown types: BucketType.default > global for your bot on all servers (if used 1 on server 1 and another on server 2, it stops), ~.user > for a user on any server, ~.member > for user on a defined guild,
    @guild_only()
    async def roll_dice(
        self, ctx, rolls_input: Optional[str]
    ):  # ya5od str wey7awwelo le int,lw mnf34 2eddy error,lw 2ktr mn 25 2eddy error, lw mfe4 2ollo 3yz kam ya m3rs
        if not rolls_input:
            await ctx.send(
                f"How many rolls?\ntype `{self.bot.PREFIX}dice num_of_rolls`"
            )
            return  # 34an ytl3 mel function mykml4

        try:
            rolls_num = int(rolls_input)
            if rolls_num > 25:
                await ctx.send(
                    f"Too many rolls. Don't roll more than 25 times."
                )
                return
            else:
                count = 0
                roll_list = list()
                for rollaya in range(rolls_num):
                    roll_result = randint(1, 6)
                    count += roll_result
                    roll_list.append(str(roll_result))

                await ctx.send(
                    f"Here's you dice roll:\n{' + '.join([r for r in roll_list])} = {count}"
                )
        except:
            await ctx.send("enter a number ffs.")

        # if rolls_num <= 25:
        #     rolls = [randint(1, 6) for i in range(rolls_num)]
        #     await ctx.send(
        #         f"They see me rollin... They hatin...\n{' + '.join([str(r) for r in rolls])} = {sum(rolls)}"
        #     )

    @command(name="greet", aliases=["welcome"], brief="greet another member")
    @guild_only()
    async def greet_member(
        self,
        ctx,
        member: Member,
        *,
        reason: Optional[str] = "They're new to the server",
    ):  # cmd: m'greet @t0va for being a hoe, member should be a discord Member object for the mention, * gets all the reason string instead of just 'for' and it's optional and should be a string
        await ctx.message.delete()
        if member == ctx.author:
            await ctx.send(f"You can't greet yourself {member.mention}?")
        else:
            await ctx.send(
                f"**{ctx.author.name}** greeted **{member.mention}** because {reason}. Say Hi!"
            )  # Member.mention mentions the specified member in the sent msg
        # author.mention >> mentions, author.name >> username, author.display_name >> name on server, author.nick >> nickname and can return "None" if there isn't any, author.id >> user's id

    @greet_member.error
    @guild_only()
    async def greet_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send(r"Who's that?")

    @command(
        name="poll",
        aliases=["vote"],
        brief="make a poll, min 2 choices max 10 choices",
    )
    @guild_only()
    async def poll(self, ctx, *, input_text: Optional[str]):
        if not input_text:
            return await ctx.send(
                f"Use `{self.bot.PREFIX}poll poll_title|option_1|option_2`.\nMax 10 options, min 2 options"
            )
        parsed = input_text.split("|")

        if len(parsed) < 3 or len(parsed) > 11:
            return await ctx.send(
                f"Use `{self.bot.PREFIX}poll poll_title|option_1|option_2`.\nMax 10 options, min 2 options."
            )
        else:
            title = parsed[0]
            options_list = parsed[1:]
            poll_reacts = num_emojis[0 : len(options_list)]
            options_votes_txt = "\n\n\n".join(
                [
                    f"{poll_reacts[i]} : {options_list[i]}"
                    for i in range(len(options_list))
                ]
            )

            poll_embed = Embed(
                title=f"{title.upper()}",
                description=options_votes_txt,
                colour=ctx.author.colour,
                timestamp=datetime.now(),
            )
            poll_embed.set_footer(
                text=f"a poll from {str(ctx.author)}",
                icon_url=ctx.author.avatar_url,
            )

            try:
                await ctx.message.delete()
            except:
                pass
            poll_msg = await ctx.send(embed=poll_embed)
            for react in poll_reacts:
                await poll_msg.add_reaction(react)

    @command(
        name="kanye",
        aliases=["ye", "yeezus", "yezus", "kny", "kanye_quote"],
        brief="a kanye quote",
    )
    @guild_only()
    async def kanye(self, ctx):
        api_url = "https://api.kanye.rest/"
        # making an async request function from aiohttp
        # using with/as for resource handling and less errros
        async with request("GET", url=api_url) as response:
            if response.status == 200:  # means the request is ok
                data = (
                    await response.json()
                )  # the json that we returned from the GET request
                # on the form of {'quote':"I'm in love with a pornstar"}
                quote = data["quote"]
                # await ctx.send(f"{quote}")
                ye_embed = Embed(title=f'"{quote}"', colour=ctx.author.colour)
                ye_embed.set_author(
                    name="A quote from Kanye West",
                    icon_url=r"https://i.imgur.com/uh9YJhb.jpg",
                )
                await ctx.send(embed=ye_embed)
            else:
                await ctx.send(f"API returned {response.status} status.")

    @command(
        name="weather",
        aliases=["temperature", "temp", "gaw", "7arara"],
        brief="fetches cairo weather",
    )
    @cooldown(rate=2, per=300, type=BucketType.user)
    @guild_only()
    async def weather(self, ctx):
        # GET api.openweathermap.org/data/2.5/weather?q=Cairo&units=metric&appid={appid}
        api_endpoint = r"https://api.openweathermap.org/data/2.5/weather"
        # ?q={city}&units=metric&appid={appid}"

        async with request(
            "GET",
            url=api_endpoint,
            params={
                "lat": "30.033333",
                "lon": "31.233334",
                "units": "metric",
                "appid": server.get("openweather_appid"),
            },
        ) as response:
            if response.status != 200:  # ok-request
                data = await response.json()

                w_dict = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "general_weather": data["weather"][0]["description"],
                    "temp": data["main"]["temp"],
                    "feels": data["main"]["feels_like"],
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                }

                w_embed = Embed(
                    title="Weather Now",
                    colour=ctx.author.colour,
                    timestamp=datetime.now(),
                )
                fields_to_add = [
                    (
                        f"{w_dict['city']}, {w_dict['country']}",
                        f"{w_dict['general_weather']}",
                        True,
                    ),
                    (
                        f"Temperature: {w_dict['temp']} C",
                        f"feels like: {w_dict['feels']} C",
                        False,
                    ),
                    (
                        f"Max: {w_dict['temp_max']}  C",
                        f"min: {w_dict['temp_min']}  C ",
                        True,
                    ),
                    (
                        f"Humidity: {w_dict['humidity']}%",
                        f"wind speed: {w_dict['wind']} km/hr",
                        False,
                    ),
                ]
                for name, val, inline_bln in fields_to_add:
                    w_embed.add_field(name=name, value=val, inline=inline_bln)
                w_embed.set_author(
                    name="openweathermap",
                    icon_url="https://imgur.com/icnPNgA.png",
                )
                w_embed.set_image(
                    url="https://media2.giphy.com/media/QRhtqYeEywJI4/giphy.gif"
                )
                await ctx.send(embed=w_embed)

            elif response.status == 401:
                await ctx.send("401: There's an API key error.\nContact t0va.")
            elif response.status == 404:
                await ctx.send(r"404: Enter a valid city name")
            elif response.status == 402:
                await ctx.send(r"402: You're using the command too much")

    @Cog.listener()  # a decorator that listens to events, IT'S NOT SELF.LISTENER
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun_stuff")
        else:
            print("fun_stuff cog loaded")

    @Cog.listener()
    async def on_message(self, Message: Message):
        if not Message.author.bot:
            if isinstance(Message.channel, channel.DMChannel):
                return
            # LIGMA
            regex_query = "|".join([key for key in ligma_dict.keys()])
            found_list = findall(regex_query, (Message.content).lower())
            if len(found_list) > 0:
                key_to_ins = found_list[
                    0
                ]  # only gives result to the first match
                goteem_line = ligma_dict[key_to_ins]
                await Message.channel.send(f"{goteem_line}\nGOTEEEM")


def setup(bot):  # hnzbt 2el bot 3al cog
    bot.add_cog(FunStuff(bot))


#############################################################################################################################

diq_piqs = [
    "https://i.4cdn.org/hm/1624293062434s.jpg",
    "https://i.4cdn.org/hm/1624293091272.jpg",
    "https://i.4cdn.org/hm/1624293122639.jpg",
    "https://i.4cdn.org/hm/1624293152274s.jpg",
    "https://i.4cdn.org/hm/1624293219932s.jpg",
    "https://i.4cdn.org/hm/1624295352802s.jpg",
    "https://i.4cdn.org/hm/1624295386778s.jpg",
    "https://i.4cdn.org/hm/1624391218033s.jpg",
    "https://i.4cdn.org/hm/1624475547503s.jpg",
    "https://i.4cdn.org/hm/1624475586913s.jpg",
    "https://i.4cdn.org/hm/1624475716668s.jpg",
    "https://i.4cdn.org/hm/1624526484439s.jpg",
    "https://i.4cdn.org/hm/1624525598539s.jpg",
    "https://i.4cdn.org/hm/1624649279801s.jpg",
    "https://i.4cdn.org/hm/1624649579476.jpg",
    "https://i.4cdn.org/hm/1624649823014.jpg",
    "https://i.4cdn.org/hm/1624649869223.jpg",
    "https://i.4cdn.org/hm/1624649926895.jpg",
    "https://i.4cdn.org/hm/1624650034482s.jpg",
    "https://i.4cdn.org/hm/1624650224494.jpg",
    "https://i.4cdn.org/hm/1624650633941.jpg",
]

ligma_dict = {
    "ligma": "ligma nuts!",
    "boffa": "can boffa deez nuts fit in yo mouf?!",
    "sugma": "sugma dique!",
    "eatma": "eatma dique!",
    "kisma": "kisma dique!",
    "stigma": "stigma dique in yo mouf!",
    "fondalma": "fondal ma nuts!",
    "tugunma": "tugunma dique!",
    "slobonma": "slobonma knob biiish!",
    "jergma": "jergma dique off biish!",
    "bofadese": "can bofadese nuts fit in yo mouf?!",
    "sugondese": "sugondese nuts!",
    "rubondese": "rubondese nuts!",
    "rydon": "rudon ma dique!",
    "won a pound": "i won a pound yo mama!",
    "candice": "candice nuts fit in yo mouf?!",
    "wilma": "wilma dique fit in yo mouf?!",
    "cds": "cds nuts? fit em in yo mouf!",
    "shogun": "shogun ma dique!",
    "e10": "e10 ma NUTS bitch!",
    "deez": "DEEZ NUTS!",
    "dragon": "dragon DEEZ NUTS!",
    "chokon": "chokon DEEZ NUTS!",
    "chockon": "chockon DEEZ NUTS!",
    "deez": "DEEZ NUTS!",
}

num_emojis = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "\N{KEYCAP TEN}",
]
