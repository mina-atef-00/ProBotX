from os import environ
from typing import ContextManager, Optional, Union
from aiohttp import request
from discord.ext.commands.core import guild_only

from src.data_clusters.configuration.server_vars import server
from discord import Member, Reaction, Embed, channel, colour
from discord.ext.commands import Cog, bot, command, cooldown, BucketType
from DiscordUtils.Pagination import CustomEmbedPaginator


async def pic_fetcher(
    query, orientation: str, pic_count: Union[int, str], api_endpoint
):
    fetcher_pics_list = list()
    async with request(
        "GET",
        url=api_endpoint,
        params={
            "query": query,
            "orientation": orientation,
            "client_id": server.get("unsplash_access_key"),
            "count": str(pic_count),
            "content_filter": "low",
        },
    ) as response:
        if response.status in (401, 405, 404):
            return None
        elif response.status == 200:  # ok-request
            rtrvd_data = await response.json()

            for pic_num in range(int(pic_count)):
                fetcher_pics_list.append(
                    {
                        "color": int((rtrvd_data[pic_num]["color"])[1:], 16),
                        "resolution": f"{rtrvd_data[pic_num]['width']}x{rtrvd_data[pic_num]['height']}",
                        "description": rtrvd_data[pic_num]["description"],
                        "url_full": rtrvd_data[pic_num]["urls"]["full"],
                        "url_regular": rtrvd_data[pic_num]["urls"]["regular"],
                        "url_small": rtrvd_data[pic_num]["urls"]["small"],
                        "user_name": rtrvd_data[pic_num]["user"]["name"],
                        "user_link": rtrvd_data[pic_num]["user"]["links"][
                            "html"
                        ],
                    }
                )
        return fetcher_pics_list


def wall_embeds(list_of_json: Optional[list]):
    if not list_of_json:
        return None

    wall_embeds_list = list()
    for wall in list_of_json:
        wall_embed = Embed(
            title=f"Unsplash Wallpapers",
            colour=wall["color"],
            description=f"{wall['description'] or 'No Description'}\n{wall['resolution']}",
        )
        wall_embed.set_author(
            name=f"by {wall['user_name']}",
            url=f"{wall['user_link']}",
            icon_url=r"https://user-images.githubusercontent.com/5659117/53183813-c7a2f900-35da-11e9-8c41-b1e399dc3a6c.png",
        )
        wall_embed.set_image(url=wall["url_regular"])
        wall_embed.add_field(
            inline=False,
            name="download",
            value=f"[full]({wall['url_full']}) | [regular]({wall['url_regular']}) | [small]({wall['url_small']})",
        )
        wall_embed.set_footer(
            text=f"{list_of_json.index(wall)+1} of {len(list_of_json)} wallpapers"
        )

        wall_embeds_list.append(wall_embed)

    return wall_embeds_list


class UnsplashEmbeds:
    def __init__(
        self, query: str = "", orientation: str = "", pic_count: int = 30
    ) -> None:
        self.query = query
        self.orientation = orientation
        self.pic_count = pic_count
        self.api_endpoint = "https://api.unsplash.com/photos/random/"

    async def pics(self):
        self.pics_list = await pic_fetcher(
            query=self.query,
            orientation=self.orientation,
            api_endpoint=self.api_endpoint,
            pic_count=self.pic_count,
        )
        return self.pics_list


class Unsplash(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("unsplash")
        else:
            print("unsplash cog loaded")

    @command(
        name="unsplash",
        aliases=["wall", "wallpaper", "splash", "background"],
        brief="fetch wallpapers from unsplash",
    )
    @guild_only()
    @cooldown(rate=3, per=600, type=BucketType.user)
    async def unsplash(self, ctx, *, search_term=""):
        wallpapers = UnsplashEmbeds(query=search_term)
        wall_list = await wallpapers.pics()
        embed_list = wall_embeds(wall_list)

        paginator = CustomEmbedPaginator(
            ctx, remove_reactions=True, timeout=180
        )
        pag_reacts = [
            ("⏮️", "first"),
            ("⏪", "back"),
            ("🔐", "lock"),
            ("⏩", "next"),
            ("⏭️", "last"),
        ]
        for emj, cmd in pag_reacts:
            paginator.add_reaction(emoji=emj, command=cmd)

        try:
            await paginator.run(embed_list)
        except:
            await ctx.send("No results found.")


def setup(bot):
    bot.add_cog(Unsplash(bot))
