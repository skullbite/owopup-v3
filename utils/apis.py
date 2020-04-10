import aiohttp, discord, json, random
from discord.ext.commands import Context
from disputils import BotEmbedPaginator

class ContextError(Exception):
    pass

class TooManyTags(Exception):
    pass

class ForbiddenTag(Exception):
    pass

class NotFound(Exception):
    pass

paste_data = {
    "api_option": "paste",
    "api_dev_key": "",
    "api_paste_code": "",
    "api_paste_format": "python",
    "api_user_key": "",
    "api_paste_private": "2",
    "api_paste_expire_date": "10M",
    "api_paste_name": "owopup eval thingy"
}
    
async def makepaste(ctx, code: str):
    paste_data["api_paste_code"] = code
    paste_data["api_dev_key"] = ctx.bot.config.pdev
    paste_data["api_user_key"] = ctx.bot.config.puser
    async with aiohttp.ClientSession() as cs:
        async with cs.post("https://pastebin.com/api/api_post.php", data=paste_data) as paste:
            gimme = await paste.text()
            return gimme

async def e621(tags: str, ctx: Context=None, NSFW=True, to_discord=False, limit=50, filetype=None, random_search=False):
    tags = tags.split(" ")
    tag_limit = 40
    if NSFW:
        pass
    else:
        tag_limit -= 1
        tags.insert(0, "rating:s")
    if filetype:
        tag_limit -= 1
        tags.insert(0, f"filetype:{filetype}")
    if not random_search:
        tag_limit -= 1
        tags.insert(0, "order:score")
    else:
        tag_limit -= 1
        tags.insert(0, "order:random")
    if len(tags) > tag_limit:
        raise TooManyTags(f"Too Many Tags Requested. (Max {tag_limit})")
    nonotags = ["scat", "cub", "young", "gore", "beastiality", "bestiality", "rape"]
    for tag in tags:
        if tag in nonotags:
            raise ForbiddenTag(f"Inapproiate tag in query: {tag}")
    tags = "%20".join(tags)
   
    if NSFW:
        reqfrom = "e621"
        
    else:
        reqfrom = "e926"
    
    async with aiohttp.ClientSession(headers={'User-Agent': 'owopup/3.0 (skullbite)'}) as eee:
        async with eee.get(f"https://{reqfrom}.net/posts.json?tags={tags}&limit={limit}") as load:
           load = await load.json()
           load = load.get("posts")
    #r.get(f"https://{reqfrom}.net/posts.json?tags={tags}%20order:score&limit={limit}", headers={'User-Agent': 'owopup/2.0 (skullbite)'})   

    if load == []:
        raise NotFound("No results for query found.")
    posts = []
    for post in load:
        for tag in post.get('tags').get('general'):
            if tag in nonotags:
                add = False
            else:
                add = True
        if add:
            posts.append({'artist': post.get("tags").get('artist'),
            'image': post.get('file').get('url'),
            'id': post.get('id'),
            'r': post.get('rating'),
            'score': post.get('score').get('total'),
            'post': f"https://{reqfrom}.net/posts/" + str(post.get('id')),
            'filetype': post.get("file").get("ext")})
        else:
            pass
    
    
        
    #properformats = [".png", ".jpg", ".jpeg", ".gif"]
    #for x in properformat:
    #   if x in read['image']:
    #        pass
            
    
    if to_discord:
        embeds = []
        for read in posts:
            if read['r'] == "s":
                color = discord.Color.green()
                rating = 'Safe'
            elif read['r'] == "q":
                color = discord.Color.gold()
                rating = 'Questionable'
            else:
                color = discord.Color.red()
                rating = 'Explicit'

            title = f"#{read['id']}: " + str(", ".join(read['artist'])).replace("_", "\_")
            if len(title) > 256:
                title = f"#{read['id']}: Too many artists to list..."
            embed = discord.Embed(title=title, url=read['post'], color=color).set_footer(text=f"Rating: {rating} | Score: {str(read['score'])}", icon_url="https://e621.net/favicon-32x32.png")

            goodfiles = ["jpg", "png", "gif"]
            if read['filetype'] in goodfiles:
                embed.set_image(url=read['image'])
            else:
                if read['filetype'] == "swf":
                    embed.description = "(This appears to be a flash animation, click the link above to view it.)"
                else:
                    embed.description = "(This appears to be a video, click the link above to view it.)"
            embeds.append(embed)
        
        if ctx == None:
            raise ContextError("No context provided.")
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        paginator = BotEmbedPaginator(ctx, embeds)
        return await paginator.run()

    else:
        #print(posts)
        if len(posts) == 1:
            return posts[0]
        return posts

class furry:
    async def bot(ctx, action: str, user: discord.User):
        bot = ctx.bot
        if ctx.channel.nsfw:
            type = 'nsfw'
        else:
            type = 'sfw'
        if ctx.author == user and type == 'nsfw' and action in ['hug', 'kiss', 'lick', 'cuddle']:
            return await ctx.send(f'Maybe someone other than yourself {ctx.author.name}..?')
        elif ctx.author == user and type == 'sfw':
            return await ctx.send(f'Maybe someone other than yourself {ctx.author.name}..?')
        valid_sfw_actions = ['boop', 'cuddle', 'fursuit', 'hold', 'hug', 'kiss', 'lick', 'propose']
        valid_nsfw_actions = ['bulge', 'bang', 'dicks', 'straight', 'cuddle', 'group', 'hug', 'kiss', 'boop', 'lick', 'suck', 'gay']
        if type == 'sfw':
            if not action.lower() in valid_sfw_actions:
                raise Exception("Invalid action raised.")
        elif type == 'nsfw':
            if not action.lower() in valid_nsfw_actions:
                raise Exception("Invalid action raised.")
        interactions = json.load(open('./utils/interactions.json'))
        if action == 'straight':
            toreq = f'https://api.furry.bot/furry/{type}/yiff/straight'
        elif action == 'gay':
            toreq = f'https://api.furry.bot/furry/{type}/yiff/gay'
        elif action == 'boop':
            toreq = f'https://api.furry.bot/furry/sfw/boop'
        else:
            toreq = f'https://api.furry.bot/furry/{type}/{action}'
        async with aiohttp.ClientSession() as owo:
            async with owo.get(toreq) as img:
                try:
                    img = await img.json()
                except Exception as e:
                    raise Exception("Invalid Return, perhaps api.furry.bot is down.")
                em = discord.Embed(color=interactions[action]['color'])
                em.title = str(random.choice(interactions[action]['responses'])).format(ctx.author.name, user.name)
                if ctx.channel.nsfw:
                    em.set_image(url=img["response"]["image"])
                else:
                    if bot.settings.get(ctx.guild.id)["images"]:
                        em.set_image(url=img["response"]["image"])
                

                #if action == 'gay':
                #    em.set_footer(text="N")
                #else:
                #    pass
                try:
                    return await ctx.send(embed=em)
                except:
                    await ctx.send("Looks like i'm not allowed to send embeds. Please go to my role and enable the permission: `EMBED_LINKS`")