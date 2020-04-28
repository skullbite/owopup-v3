import discord, traceback, aiohttp, asyncio, requests
from discord.ext import commands
from discord.ext.commands import errors

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.post())
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if not self.bot.is_ready():
            return
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            if ctx.command.root_parent:
                cmd_name = str(ctx.command.root_parent) + " " + str(ctx.command.name)
            else:
                cmd_name = ctx.command.name
            await ctx.invoke(self.bot.get_command("help"), cm=cmd_name)
            

        elif isinstance(err, errors.CommandNotFound):
            pass
        elif isinstance(err, errors.BotMissingPermissions):
            await ctx.send(f"I'm missing permissions to run this command: `{' '.join(err.missing_perms)}`\nPlease make sure I have these before trying again.")
        elif isinstance(err, errors.MissingPermissions):
            print("uhhh")
            await ctx.send(f"You're missing permissions to run this command: `{' '.join(err.missing_perms)}`\nPlease make sure you have these before trying again.")
        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send("This command can't be use in dms. sowwy")
        elif isinstance(err, errors.CommandOnCooldown):
            if self.bot.abuse[f"{ctx.author.id}_{ctx.command.name}"] == 5:
                
                self.bot.blacklist.create(ctx.author, "`[AUTO]` spamming commands")
                print('└[RATELIMITED]')
                return await ctx.send("You've been blacklisted from commands for spamming them. You may use commands again in 15 minutes.")
            await ctx.send(f"Slow your roll. This command can't be used again for another {err.retry_after:.0f} seconds.")
            print('└[COOLDOWN]')
        elif isinstance(err, errors.CommandInvokeError):
            err = err.original
            if str(type(err).__name__) == "Forbidden":
                return
            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = ''.join(_traceback)
            #error = ('`{}` - `{}`').format(type(err).__name__, err)
            rec_error = ('```py\n{2}{0}: {3}\n```').format(type(err).__name__, ctx.message.content, _traceback, err)
            short = discord.Embed(color=self.bot.color, title="Error Occured.")
            print('└[ERR]')
            if self.bot.config.owner == ctx.author.id:
                short.description = rec_error
            else:
                full = discord.Embed(title="Error Occurred", description=f"Command: {ctx.command.name}\nFull Message: {ctx.message.content}\nNSFW? {ctx.channel.nsfw if ctx.guild else True}\nFull Trace: {rec_error}")
                short.description = "An error has occurred while running this command. - Join our [Support Server](http://discord.gg/c4vWDddP) if you have any further questions."
                self.bot.webhook.send(embed=full)
            await ctx.send(embed=short)
            
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Ready: {self.bot.user} | Guilds: {len(self.bot.guilds)}")
        await self.bot.change_presence(activity=discord.Game(type=0, name="Enjoying V3 | owo announcement"), status=discord.Status.online)
        self.bot.webhook = discord.Webhook.from_url(self.bot.config.webhook, adapter=discord.RequestsWebhookAdapter())
        self.bot.webhook.send(f"*`[i]`* **{self.bot.user} is ready.**")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        b = len([x for x in guild.members if x.bot])
        sketchy = "\n*`[!]`* This server has more members than bots.\n" if guild.member_count < (guild.member_count - b) else "\n"
        self.bot.webhook.send(f"*`[+]`* **Joined {guild.name}** ({guild.id})\n*`[+]`* Total Guilds: {len(self.bot.guilds)}{sketchy}*`[+]`* Guilds in shard #{guild.shard_id}: {len([x for x in self.bot.guilds if x.shard_id == guild.shard_id])}".replace("@", "@‎"))
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.webhook.send(f"*`[-]`* **Lost {guild.name}** ({guild.id})\n*`[-]`* Total Guilds: {len(self.bot.guilds)}\n*`[-]`* Guilds in shard #{guild.shard_id}: {len([x for x in self.bot.guilds if x.shard_id == guild.shard_id])}".replace("@", "@‎"))
    
    async def post(self):
        if not self.bot.is_ready() or not self.bot.user.id == 365255872181567489: # Beta Reasons
            return

        payload = {"server_count": len(self.bot.guilds), "shard_count": len(self.bot.shards)}
        payload2 = {"guildCount": len(self.bot.guilds), 'shardCount': len(self.bot.shards)}
        payload3 = {"guildCount": len(self.bot.guilds)}
        async with aiohttp.ClientSession() as send:
            await send.post(f"https://top.gg/api/bots/{self.bot.user.id}/stats", headers={"Authorization": self.bot.config.listtokens.dbl}, data=payload)
            await send.post(f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats", headers={"Authorization": self.bot.config.listtokens.botsgg}, data=payload2)
            await send.post(f"https://botsfordiscord.com/api/bot/{self.bot.user.id}", headers={"authorization": self.bot.config.listtokens.bfd}, data=payload)
            await send.post(f"https://bots.ondiscord.xyz/bot-api/bots/{self.bot.user.id}/guilds", headers={"Authorization": self.bot.config.listtokens.bod}, data=payload3)
        await asyncio.sleep(600)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            print(f"[{ctx.guild.shard_id}][User: {ctx.author} ({ctx.author.id})][Command: {ctx.command.name}]")
        except:
            print(f"[DM][User: {ctx.author} ({ctx.author.id})][Command: {ctx.command.name}]")
        
        self.bot.stats["cmds_used"] += 1
        self.bot.cmds[ctx.command.name] += 1
        if ctx.command.is_on_cooldown:
            self.bot.abuse[f"{ctx.author.id}_{ctx.command.name}"] += 1
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.abuse[f"{ctx.author.id}_{ctx.command.name}"] = 0

def setup(bot):
    bot.add_cog(Events(bot))
