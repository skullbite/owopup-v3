from discord.ext import commands
from pymongo import MongoClient
from colorama import Style, Fore
from collections import Counter, namedtuple
import json, os, datetime, discord


def warning(text):
    print("\033[1m" + Fore.RED + text + Style.RESET_ALL)


config = json.load(
    open("config.json"), object_hook=lambda d: namedtuple("X", d.keys())(*d.values())
)
db = MongoClient(config.mongostr).owopup


def get_prefix(bot, msg):
    if not msg.guild:
        return commands.when_mentioned_or("owo ")(bot, msg)
    try:
        settings = bot.settings.get(msg.guild.id)
        prefix = settings["prefix"]
        if not prefix:
            return commands.when_mentioned_or("owo ")(bot, msg)
        return commands.when_mentioned_or(prefix)(bot, msg)
    except Exception:
        return commands.when_mentioned_or("owo ")(bot, msg)


class pupper(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=get_prefix, case_insenitive=True, *args, **kwargs
        )
        self.color = 2444566
        self.db = db
        self.config = config
        self.stats = Counter()
        self.cmds = Counter()
        self.abuse = Counter()
        self.settings_cache = {}
        self.uptime = datetime.datetime.utcnow()

        class settings:
            def get(id: int):
                try:
                    return self.settings_cache[str(id)]
                except:
                    settings = self.db.settings.find_one({"id": id})
                    if not settings:
                        defaults = {
                            "modlog": None,
                            "mutedrole": None,
                            "prefix": None,
                            "images": False,
                            "id": id,
                        }
                        self.db.settings.insert_one(defaults)  # AAA I HATE THIS
                        return self.db.settings.find_one({"id": id})
                    return settings

            def init_settings(guild: discord.Guild):
                if self.db.settings.find_one({"id": guild.id}):
                    raise Exception("Guild already has settings.")
                defaults = {
                    "modlog": None,
                    "mutedrole": None,
                    "prefix": None,
                    "images": False,
                    "id": guild.id,
                }
                self.db.settings.insert_one(defaults)
                self.cache()

            def edit(guild: discord.Guild, key, value):
                self.db.settings.update({"id": guild.id}, {"$set": {key: value}})
                self.cache()

        def cache():
            self.settings_cache = {}
            for x in self.db.settings.find():
                self.settings_cache[str(x["id"])] = x

        self.cache = cache
        self.settings = settings
        # class modlog:
        #    def get_cases(id: int):
        #        cases = []
        #        for x in bot.db.modlogs.find({"guild_id": id}):
        #            cases.append(x)
        #        return cases

        #    def make_case(guild)
        class blacklist:
            def check(id: int):
                bad = self.db.blacklist.find_one({"id": id})
                if not bad:
                    raise Exception("No entry found.")
                return bad

            def create(user: discord.User, reason: str, revoke_at=15, permanent=False):
                if self.db.blacklist.find_one({"id": user.id}):
                    raise Exception("User is already in blacklist.")
                revoke_at = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=revoke_at
                )
                if permanent:
                    revoke_at = 0
                self.db.blacklist.insert_one(
                    {
                        "id": user.id,
                        "reason": reason,
                        "at": datetime.datetime.utcnow(),
                        "permanent": permanent,
                        "revoke_at": revoke_at,
                    }
                )

            def remove(user: discord.User):
                if not self.db.blacklist.find_one({"id": user.id}):
                    raise Exception("No Entry Found.")
                return self.db.blacklist.delete_one({"id": user.id})

            def timestring(*, brief=False, time=self.uptime):
                now = datetime.datetime.utcnow()
                if time == self.uptime:
                    delta = now - time
                else:
                    delta = time - now
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)

                if not brief:
                    if days:
                        fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
                    else:
                        fmt = "{h} hours, {m} minutes, and {s} seconds"
                else:
                    fmt = "{h}h {m}m {s}s"
                if days:
                    fmt = "{d}d " + fmt

                return fmt.format(d=days, h=hours, m=minutes, s=seconds)

        self.blacklist = blacklist


bot = pupper()


@bot.event
async def on_message(msg):
    if not bot.is_ready() or msg.author.bot:
        return
    ctx = await bot.get_context(msg)
    if ctx.command:
        entry = bot.db.blacklist.find_one({"id": ctx.author.id})
        if entry:
            if (
                entry["revoke_at"] <= datetime.datetime.utcnow()
                and not entry["permanent"]
            ):
                bot.blacklist.remove(msg.author)
                return await bot.process_commands(msg)

            timer = (
                f"Revoke in: {bot.blacklist.timestring(time=entry['revoke_at'], brief=True)}"
                if not entry["permanent"]
                else "**This case is permanent.**"
            )
            return await ctx.send(
                f"You've been blacklisted.\nReason: {entry['reason']}\n{timer}"
            )

    if msg.content == f"<@!{bot.user.id}>" or msg.content == f"<@{bot.user.id}>":
        await ctx.send(
            f"Huh? Did you want something..? My help command can be ran with `{bot.command_prefix(bot, msg)[2]}help`"
        )

    await bot.process_commands(msg)


@bot.event
async def on_message_edit(b, a):
    if not bot.is_ready() or a.author.bot or b.content == a.content:
        return
    ctx = await bot.get_context(a)
    if ctx.command:
        entry = bot.db.blacklist.find_one({"id": ctx.author.id})
        if entry:
            if (
                entry["revoke_at"] <= datetime.datetime.utcnow()
                and not entry["permanent"]
            ):
                bot.blacklist.remove(ctx.author)
                return await bot.process_commands(a)
            return
    await bot.process_commands(a)


print("Getting ready...")
for x in os.listdir("cogs"):
    if not x.endswith(".py"):
        continue
    file = x.replace(".py", "")
    try:
        bot.load_extension(f"cogs.{file}")
        print(f"Loaded {file}")
    except Exception as e:
        warning(f"Failed to load {file}: {e}")


bot.run(config.token)
