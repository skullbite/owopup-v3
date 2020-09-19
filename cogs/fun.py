from discord.ext import commands
from utils.apis import *


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["e9"])
    async def e926(self, ctx, tags: str):
        """Searches for posts from e926.net"""
        try:
            await e621(tags=tags, ctx=ctx, NSFW=False, to_discord=True)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    async def hug(self, ctx, user: discord.User):
        """Give someone a hug"""
        if user == self.bot.user:
            return await ctx.send("i-i'm good on hugs.. thank you though..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "hug", user)

    @commands.command()
    @commands.guild_only()
    async def cuddle(self, ctx, user: discord.User):
        """Cuddle someone"""
        if user == self.bot.user:
            return await ctx.send("dunno w-why you'd want to cuddle me..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "cuddle", user)

    @commands.command()
    @commands.guild_only()
    async def kiss(self, ctx, user: discord.User):
        """Give someone a kiss"""
        if user == self.bot.user:
            return await ctx.send("you're too sweet r-really..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "kiss", user)

    @commands.command()
    @commands.guild_only()
    async def boop(self, ctx, user: discord.User):
        """"Boop someones snout"""
        if user == self.bot.user:
            return await ctx.send("you don't wanna boop me.. my s-snout's weird..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "boop", user)

    @commands.command()
    @commands.guild_only()
    async def hold(self, ctx, user: discord.User):
        """"Hold someone tight"""
        if user == self.bot.user:
            return await ctx.send("why me..?")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "hold", user)

    @commands.command()
    @commands.guild_only()
    async def lick(self, ctx, user: discord.User):
        """"Put your tongue on someone"""
        if user == self.bot.user:
            return await ctx.send("don't lick me..! my fur is better dry..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        await furry.bot(ctx, "boop", user)

    @commands.guild_only()
    async def pat(self, ctx, user: discord.User):
        """Give someone a pat on the head"""
        if user == self.bot.user:
            return await ctx.send("thanks for the pats..")
        if user == ctx.author:
            return await ctx.send("Maybe someone other than yourself?")
        post = await e621(
            tags="head_pat", NSFW=False, limit=1, filetype="jpg", random_search=True
        )
        embed = discord.Embed(
            color=self.bot.color,
            description=f"{ctx.author.name} pat {user.name} on the head for being a cute heck",
        )
        embed.set_image(url=post["image"])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
