from discord.ext import commands
import os, discord, time, psutil

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
    
    @commands.command(aliases=["?"])
    async def help(self, ctx, *, cm: str=None):
        """The help command. duh."""
        embed = discord.Embed(color=self.bot.color)
        paws = self.bot.get_emoji(478418730683072542)
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        dont_show = ['Events', 'Owner']
        if not cm:
            cogs = list(self.bot.cogs)
            for x in dont_show:
                if x in cogs:
                    cogs.remove(x)
            mods = '\n• '.join(cogs)
            mods = f"• {mods}"
            embed.title = f"{paws} Hewwo {ctx.author.name}, I'm {self.bot.user.name}! {paws}"
            embed.description = f"Call me the dog with all the owos.\nUse `{ctx.prefix}help <command/module>` to get help on a command or the commands of a modules.\n\nAll of my modules are listed below:\n{mods}"
            embed.description = embed.description.replace(f"<@{self.bot.user.id}>", f"@{self.bot.user.name}").replace(f"<@!{self.bot.user.id}>", f"@{self.bot.user.name}")
            inv = discord.utils.oauth_url(self.bot.user.id) + "268463110"
            embed.add_field(name="Invite", value=f"[click here]({inv})")
            return await ctx.send(embed=embed)
        
        cmd = self.bot.get_command(cm)
        if not cmd:
            mod = self.bot.get_cog(cm)
            dont_show = ['Events', 'Owner']
            if cm in dont_show and ctx.author.id == self.bot.config.owner:
                return await ctx.send("Sorry you can't view this module's commands.")
            if not mod:
                await ctx.send("No command or module found.") 
                return
            cmds = mod.get_commands()
            cmds = "\n".join([f"``{x.name}`` - {x.help}" for x in cmds])
            embed.title = f"{paws} {cm.title()} Commands {paws}"
            embed.description = cmds
            await ctx.send(embed=embed)
        else:
            embed.title = f"{paws} Help for {cmd} {paws}"
            anarray = []
            for x in list(cmd.clean_params):
                if not str(cmd.params[x]).endswith("=None"):
                    anarray.append(f"<{x}>")
                else:
                    anarray.append(f"[{x}]")
            args = " ".join(anarray)
            args = " " + args
            try:
                subcmds = "\n```fix\n│├Subcommands:\n" + "\n".join([f"│├{x.name} - {x.help}" for x in self.bot.all_commands[cmd.name].commands]) + "```"
            except:
                subcmds = ""
            if cmd.root_parent:
                cmd_name = str(cmd.root_parent) + " " + str(cmd.name)
            else:
                cmd_name = cmd.name
            if not cmd.aliases == []:
                aliases = f"\nAliases: ``" + ", ".join(cmd.aliases) + "``"
            else:
                aliases = ""
            embed.description = f"Usage: `{ctx.prefix}{cmd_name}{args}`{aliases}\nDescription: {cmd.help}{subcmds}"
            embed.description = embed.description.replace(f"<@{self.bot.user.id}>", f"@{self.bot.user.name}").replace(f"<@!{self.bot.user.id}>", f"@{self.bot.user.name}")
            await ctx.send(embed=embed)

    @commands.command()
    async def announcement(self, ctx):
        """Shows the news about the big update!"""
        await ctx.send(f"Hewwo {ctx.author} - Welcome to owopup v3!\n**What's new?**\nThanks to new hosting we've opened up settings panel! ({ctx.prefix}settings) Along with this we've removed quite a few useless commands and cleaned up a lot of run on/pointless code, along with spam handling. Making owopup is as efficient as ever! More will come in the future.")
    
    @commands.command()
    async def ping(self, ctx):
        """Am i alive?"""
        _time = time.monotonic()
        msg = await ctx.send("Hold on lemme check...")
        _time = round((time.monotonic() - _time) * 1000)
        latency = round(self.bot.latency * 1000)
        await msg.edit(content=f"Ah. Here we go\n`MSG :: {_time}ms`\n`API :: {latency}ms`")
    
    @commands.command()
    async def invite(self, ctx):
        """Sends Bot Invite"""
        invite = discord.utils.oauth_url(self.bot.user.id) + "268463110"
        n_perms = discord.utils.oauth_url(self.bot.user.id) + "0"
        embed = discord.Embed(color=self.bot.color, description=f"[Bot Invite]({invite})\n`{' ‎' * 22}`\n[Bot Invite (No Perms)]({n_perms})\n`{' ‎' * 7}`\n[Support Server](http://discord.gg/c4vWDddP)")
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """Gets bot info"""
        ramUsage = self.process.memory_full_info().rss / 1024**2
        embed = discord.Embed(title="Here's some fun facts about me", color=self.bot.color)
        embed.add_field(name="Total Guilds", value=str(len(self.bot.guilds)))
        embed.add_field(name="RAM in use", value=f"{ramUsage:.2f} MB")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Information(bot))