from discord.ext import commands
from discord.ext.commands import errors
from utils.apis import e621, furry

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            return True
        if ctx.channel.nsfw:
            return True
        return False
    
    async def cog_command_error(self, ctx, err):
        if isinstance(err, errors.CheckFailure):
            return await ctx.send("This command can only be ran in either a NSFW channel or DMs.")


    @commands.command()
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def yiff(self, ctx, stra: str=None):
        """Shows yiff (default: gay) type "-s" after the command to view straight yiff"""
        if stra == "-s":
            await furry.bot(ctx, "straight", ctx.author)
        else:
            await furry.bot(ctx, "gay", ctx.author)
    
    @commands.command()
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def bulge(self, ctx):
        """What's this?"""
        await furry.bot(ctx, "bulge", ctx.author)
        
    @commands.command(name="e621", aliases=["e6"])
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def _e621(self, ctx, *, tags: str):
        """Searches posts from e621.net"""
        try:
            await e621(tags=tags, ctx=ctx, to_discord=True)
        except Exception as e:
            await ctx.send(e)
    
def setup(bot):
    bot.add_cog(NSFW(bot))