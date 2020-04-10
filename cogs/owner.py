from discord.ext import commands
from discord.ext.commands import errors
from utils.apis import makepaste
import ast, discord, time, os, traceback, datetime

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reboot(self, ctx):
        await ctx.send("i'll be back in a bit.")
        await self.bot.logout()
    
    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, user: discord.Member, *, command):
        """Runs a cmd under someone elses name"""
        cmd = ctx.message
        cmd.author = user
        cmd.content = ctx.prefix + command

        await self.bot.process_commands(cmd)

    @commands.command(hidden=True, aliases=["sh"])
    @commands.is_owner()
    async def shell(self, ctx, *, command: str):
        """Run commands"""
        _time = time.monotonic()
        cmd_output = os.popen(command).read()
        _time = round((time.monotonic() - _time) * 1000)
        embed = discord.Embed(title=f"Output returned in `{_time}ms`", description=f"```sh\n{cmd_output}```", color=self.bot.color)
        await ctx.send(embed=embed)

    @commands.command(name="eval", hidden=True, aliases=["ev"])
    @commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        """Eval Stuff"""
        em = discord.Embed(color=self.bot.color).set_author(name="owopup eval")
        fn_name = "_eval_expr"
        silent = False
        if cmd.endswith("-s"):
            inp = cmd.split("-s")
            del inp[len(inp) - 1]
            cmd = "-s".join(inp)
            #cmd = cmd.replace(" -s", "")
            silent = True
        cmd = cmd.strip("` ")
        em.add_field(name="📥 Input:", value=f"```py\n{cmd}```", inline=False)
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        self.insert_returns(body)
        
        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        _time = time.monotonic()
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        try:
            result = (await eval(f"{fn_name}()", env))
        except Exception as e:
            _traceback = traceback.format_tb(e.__traceback__)
            _traceback = ''.join(_traceback)
            fullerror = ('```py\n{2}{0}: {3}\n```').format(type(e).__name__, ctx.message.content, _traceback, e)
            em.add_field(name="❌ Error:", value=fullerror)
            return await ctx.send(embed=em)
        if silent:
            return
        thing = f"```py\n{result}```"
        if result == None:
            thing = "`No Return.`"
        if len(str(result)) > 1024:
            f = str(result)
            memes = await makepaste(ctx, f)
            thing = f"Sent to pastebin. {memes}"
        

        _time = round((time.monotonic() - _time) * 1000)
        em.set_footer(text=f"Returned in {_time}ms")
        
        em.add_field(name="📤 Ouput:", value=thing, inline=True)
        try:
            await ctx.send(embed=em)
        except Exception as e:
            if not result:
                return await ctx.send(f"`{e}`")

    @commands.command()
    @commands.is_owner()
    async def flirt(self, ctx, *,  c: str):
        """>w>"""
        tony = self.bot.get_user(296044953576931328)
        self.bot.c = ctx.channel
        await tony.send(c)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, file: str):
        """Loads a Cog"""
        embed = discord.Embed(color=self.bot.color)
        try:
            self.bot.load_extension(f"cogs.{file}")
            embed.title = f"Successfully loaded {file}"
        except Exception as e:
            if isinstance(e, errors.ExtensionNotFound):
                embed.title = f"Failed to load {file}: {e.original}"
            else:
                embed.title = f"Failed to load {file}: {e}"
        await ctx.send(embed=embed)
    
    @commands.group(aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        """Uhhh handles the blacklist."""
        if ctx.invoked_subcommand == None:
            if ctx.command.root_parent:
                cmd_name = str(ctx.command.root_parent) + " " + str(ctx.command.name)
            else:
                cmd_name = ctx.command.name
            cmd = ctx.message
            cmd.content = ctx.prefix + "help " + cmd_name

            await self.bot.process_commands(cmd)

    @blacklist.command()
    async def check(self, ctx, user: discord.User):
        """Checks an entry"""
        try:
            #.strftime('%-m/%-d/%y at %I:%M %p')
            entry = self.bot.blacklist.check(user.id)
            embed = discord.Embed(title="Blacklist Entry", description=f"User: {user} ({user.id})\nReason: {entry['reason']}\nHappened at: {entry['at']}\nRevoke in: {(datetime.datetime.utcnow() - entry['revoke_at'])}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @blacklist.command()
    async def add(self, ctx, user: discord.User, *, reason: str):
        """Adds an entry to the blacklist"""
        try: 
            self.bot.blacklist.create(user, reason)
            embed = discord.Embed(title="Blacklist Entry Created", description=f"User: {user} ({user.id})\nReason: {reason}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
    
    @blacklist.command()
    async def remove(self, ctx, user: discord.User):
        """Removes an entry from the blacklist"""
        try:
            entry = self.bot.blacklist.remove(user)
            embed = discord.Embed(title=f"Blacklisting has been revoked for {user}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)


    @commands.command(hidden=True, aliases=["re"])
    @commands.is_owner()
    async def reload(self, ctx, file: str):
        """Reloads a Cog"""
        embed = discord.Embed(color=self.bot.color)
        try:
            self.bot.reload_extension(f"cogs.{file}")
            embed.title = f"Successfully reloaded {file}"
        except Exception as e:
            embed.title = f"Failed to reload {file}: {e} - Using last working version of cog."
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, file: str):
        """Unloads a Cog"""
        embed = discord.Embed(color=self.bot.color)
        try:
            self.bot.load_extension(f"cogs.{file}")
            embed.title = f"Successfully unloaded {file}"
        except Exception as e:
            embed.title = f"Failed to unload {file}: {e}"
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def test(self, ctx):
        raise Exception

def setup(bot):
    bot.add_cog(Owner(bot))