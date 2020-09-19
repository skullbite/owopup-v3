from discord.ext import commands
from utils.misc import reason
import discord, datetime


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.errors.NoPrivateMessage
        return True

    async def ml(
        self,
        ctx,
        target: discord.User,
        case: str,
        reason,
        t_channel: discord.TextChannel = None,
    ):
        casetypes = {
            "unmute": 0x8534BF,
            "mute": 0xDB781A,
            "kick": 0xEDD311,
            "ban": 0xED2311,
            "unban": 0x8534BF,
            "test": 0xFFFFFF,
        }
        if t_channel:
            channel = t_channel
        else:
            ch_id = self.bot.settings.get(ctx.guild.id)["modlog"]
            if not ch_id:
                return
            channel = self.bot.get_channel(ch_id)

        embed = discord.Embed(color=casetypes[case], title=case.title())
        embed.add_field(name="Target", value=f"{target} ({target.id})", inline=True)
        embed.add_field(name="Responsible", value=str(ctx.author), inline=True)
        embed.add_field(
            name="Reason",
            value=reason if reason else "No reason specified.`",
            inline=False,
        )
        embed.timestamp = datetime.datetime.utcnow()
        try:
            await channel.send(embed=embed)
            return True
        except Exception as e:
            if case != "test":
                await ctx.send(
                    "⚠️ I couldn't send to the set modlog channel. Please consider changing the channel or making sure i can send to it."
                )
            return False

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """Shows settings for the guild"""
        if ctx.invoked_subcommand is None:
            s = self.bot.settings.get(ctx.guild.id)
            modlog = False if not s["modlog"] else True
            if not self.bot.get_channel(s["modlog"]) and modlog:
                modlog = (
                    "Possibly deleted/invisible channel. Please consider changing it."
                )
            elif self.bot.get_channel(s["modlog"]):
                modlog = self.bot.get_channel(s["modlog"]).mention
            else:
                modlog = "Not set."
            mutedrole = False if not s["mutedrole"] else True
            if mutedrole and not ctx.guild.get_role(s["mutedrole"]):
                mutedrole = "Possibly deleted role. Please consider changing it."
            elif ctx.guild.get_role(s["mutedrole"]):
                mutedrole = ctx.guild.get_role(s["mutedrole"]).mention
                if role.position >= ctx.guild.me.top_role.position:
                    mutedrole += " (This role has been placed above my highest role. I cannot assign it.)"
            else:
                mutedrole = "Not set."
            prefix = False if not s["prefix"] else True
            if prefix:
                prefix = s["prefix"]
            else:
                prefix = "owo"
            images = "On" if s["images"] else "Off"

            embed = discord.Embed(
                color=self.bot.color,
                title=f"Settings for {ctx.guild.name}",
                description=f"Modlog Channel: {modlog}\nMuted Role: {mutedrole}\nImages in RP Commands: {images}\nPrefix: {prefix}",
            ).set_footer(
                text=f'Use "{ctx.prefix}help settings" to see how to change the settings.'.replace(
                    f"<@{self.bot.user.id}>", f"@{self.bot.user.name}"
                ).replace(
                    f"<@!{self.bot.user.id}>", f"@{self.bot.user.name}"
                )
            )
            await ctx.send(embed=embed)

    @settings.command()
    async def modlog(self, ctx, *, channel: discord.TextChannel = None):
        """Sets the logging channel. Don't add a channel to remove the modlog channel."""
        if not channel:
            self.bot.settings.edit(ctx.guild, "modlog", None)
            return await ctx.send("Modlog channel has been reset.")
        msg = await ctx.send("Sending test message to channel...")
        success = await self.ml(
            ctx,
            ctx.author,
            "test",
            "Hello! If you're seeing this you've set up your modlog channel properly!",
            channel,
        )
        if success:
            self.bot.settings.edit(ctx.guild, "modlog", channel.id)
            await msg.edit(
                content=f"Test Successful!\nYour modlog channel has successfully been set to {channel.mention} (NOTE: This will only log mod actions done with owopup)"
            )
        else:
            await msg.edit(
                content=f"Test Unsuccessful.\nCouldn't send to channel. Please fix permissions and try again."
            )
            return

    @settings.command()
    async def mutedrole(self, ctx, *, role: discord.Role = None):
        """Sets the muted role. Don't add a role to remove the current muted role."""
        if not role:
            self.bot.settings.edit(ctx.guild, "mutedrole", None)
            return await ctx.send("Muted Role has been reset to none.")
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.send(
                "⚠️ I cannot assign this role because it's above my highest role. Please put it below my highest role."
            )
        if role.managed:
            return await ctx.send(
                "⚠️ I cannot assign this role because it's managed by an integration. Please choose a different role and try again."
            )
        self.bot.settings.edit(ctx.guild, "mutedrole", role.id)
        await ctx.send(f"Your muted role has successfully been set to {role.name}")

    @settings.command()
    async def prefix(self, ctx, *, prefix: str = None):
        """Sets prefix for the server.\nDon't add a prefix to reset it to default. Add --space at the end to add a space at the end.\nEx: @owopup setprefix hi --space"""
        if not prefix:
            self.bot.settings.edit(ctx.guild, "prefix", None)
            return await ctx.send(f"Prefix for this server is now reset.")
        if "--space" in prefix:
            prefix = prefix.replace("--space", "")
        if prefix == "" or prefix == " ":
            return await ctx.send("You can't set a blank prefix.")
        self.bot.settings.edit(ctx.guild, "prefix", prefix)

        await ctx.send(f"Prefix has been set to `{prefix}`.")

    @settings.command()
    async def images(self, ctx):
        """Toggles images in commands like hug, kiss etc."""
        s = self.bot.settings.get(ctx.guild.id)
        self.bot.settings.edit(ctx.guild, "images", not s["images"])
        images = "on" if s["images"] else "off"
        await ctx.send(f"Images are now turned {images}.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, _reason: str = None):
        """Kicks a member from the server."""
        try:
            await member.kick(reason=reason(ctx, _reason))
            await ctx.send(f"Bye Bye {member}!")
            await self.ml(ctx, member, "kick", _reason)
        except:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, _reason: str = None):
        """Permanently removes a member from the server."""
        try:
            await member.ban(reason=reason(ctx, _reason))
            await ctx.send(f"Bye Bye {member}! Don't come back!")
            await self.ml(ctx, member, "ban", _reason)
        except:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, _reason: str = None):
        """Revokes a ban."""
        try:
            await ctx.guild.unban(user, reason=reason(ctx, _reason))
            await ctx.send(f"I really didn't want to but {user} has been unbanned")
            await self.ml(ctx, member, "unban", _reason)
        except:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, _reason: str = None):
        """Mutes a user."""
        try:
            s = self.bot.settings.get(ctx.guild.id)
            muterole = ctx.guild.get_role(s["mutedrole"])
            if not muterole:
                return await ctx.send(
                    f"⚠️ No mute role set for this server. Set it with `{ctx.prefix}settings mutedrole`"
                )

            await member.add_roles(muterole, reason=reason(ctx, _reason))
            await ctx.send(f"{member} has been muted.")
            await self.ml(ctx, member, "mute", _reason)
        except Exception as e:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, _reason: str = None):
        """Mutes a user."""
        try:
            s = self.bot.settings.get(ctx.guild.id)
            muterole = ctx.guild.get_role(s["mutedrole"])
            if not muterole:
                return await ctx.send(
                    f"⚠️ No mute role set for this server. Set it with `{ctx.prefix}settings mutedrole`"
                )
            if not muterole in member.roles:
                return await ctx.send(
                    f"Seems the user was unmuted manually, they don't have the mute role anymore."
                )
            await member.remove_roles(muterole, reason=reason(ctx, _reason))
            await ctx.send(f"{member} has been unmuted.")
            await self.ml(ctx, member, "unmute", _reason)
        except:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )

    @commands.command(aliase=["nick"])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name=None):
        """Changes a user's nickname"""
        try:
            if len(name) > 32:
                return await ctx.send("Nickname is too long. (32 max)")
            await member.edit(nickname=name)
        except:
            await ctx.send(
                "There was an issue, make sure this person isn't above me in the role hierarchy."
            )


def setup(bot):
    bot.add_cog(Moderation(bot))