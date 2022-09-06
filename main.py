#!/usr/bin/python3
from email.policy import default
import os
import discord
from discord.utils import get
import random, time, asyncio

import funcs
import config
import visuals
import senate

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# ECONOMY
@bot.command(description="Displays your balance.")
async def balance(ctx):
    embed = funcs.create_embed(ctx, f"You have {funcs.sdb.cool_balance(ctx.author.id)} credits.")
    await ctx.respond(embed=embed, view=visuals.createSpendingButton(ctx))

@bot.command(description="Work for once in your life.")
async def work(ctx):
    if(int(funcs.sdb.get_value(ctx.author.id, 'workcd')) < int(time.time())):
        funcs.sdb.set_value(ctx.author.id, 'workcd', int(time.time() + (30 * 60)))

        prize = random.choice([100, 250, 500, 750, 1000])
        phrases = ["You mow someone's lawn.", "You sell some used condoms.",
                   "You steal an NFT.", "You gipsy someone's phone.",
                   "You sell your liver.", "You open an OnlyFans.",
                   "You steal some highschooler's lunch money.", "You rob the local homosexual.",
                   "You mine some crypto.", "You do some slurping.",
                   "You scam someone on ebay.", "You beg stormy to cheat you credits."]
        funny = random.choice(phrases)
        
        funcs.sdb.add_credits(ctx.author.id, prize)
        
        embed = funcs.create_embed(ctx, f"{funny}\nYou earned **◈{(prize)}** credits.")
        await ctx.respond(embed=embed, view=visuals.createSpendingButton(ctx))
        return

    embed = funcs.create_embed(ctx, ":x: You may not work yet.")
    await ctx.respond(embed=embed)

@bot.command(description="Transfer some credits.")
async def transfer(ctx, user: discord.Member, amount: discord.Option(int)):
    if(amount < 25):
        embed = funcs.create_embed(ctx, f":x: Please enter at least 25 credits.")
        await ctx.respond(embed=embed)
        return

    if(funcs.sdb.get_value(ctx.author.id, "credits") < int(amount)):
        embed = funcs.create_embed(ctx, f":x: You do not have {amount} credits.")
        await ctx.respond(embed=embed)
        return

    funcs.sdb.add_credits(ctx.author.id, -amount)
    funcs.sdb.add_credits(user.id, amount)

    embed = funcs.create_embed(ctx, f":white_check_mark: Transferred {amount} credits to {user.mention}.")
    await ctx.respond(embed=embed)

# FUN
@bot.command(description="Spin the slots.")
async def slots(ctx, amount: discord.Option(int)):
    await funcs.slots(ctx, amount)

@bot.command(description="Play some blackjack.")
async def blackjack(ctx, amount: discord.Option(int)):
    await funcs.blackjack(ctx, amount)

# MISC
@bot.command(description="Read the help page.")
async def help(ctx):
    helpinfo = ""
    helpinfo += ":moneybag: **ECONOMY**\n"
    helpinfo += "`bal(ance)`, `transfer/pay`, `work`"
    helpinfo += "\n\n"
    helpinfo += ":video_game: **FUN**\n"
    helpinfo += "`slots`, `blackjack/bj`, `roll`, `flip`, `me`"
    helpinfo += "\n\n"
    helpinfo += ":tada: **MISC**\n"
    helpinfo += "`ping`, `help`, `about`"
    helpinfo += "\n\n"
    helpinfo += ":clown: **DEGEN LARP**\n"
    helpinfo += "`hug`, `slap`, `rape`, `coom`"

    if(ctx.guild.id == 687732235604066366):
        helpinfo += "\n\n"
        helpinfo += "**SF Specific**\n"
        helpinfo += "`host`, `vote`, `service`"

    embed = funcs.create_embed(ctx, helpinfo, ":grey_question: Help Page")
    await ctx.respond(embed=embed)

@bot.command(description="Generate random numbers.")
async def roll(ctx, minimum: discord.Option(int, required=False, default=0), maximum: discord.Option(int, required=False, default=10)):
    n = random.randint(minimum, maximum)
    await ctx.respond(f"{ctx.author.mention} rolls a :game_die: die, computer says {n}")

@bot.command(description="Flip a coin.")
async def coin(ctx):
    await ctx.respond(random.choice(["Heads.", "Tails."]))

# DEGEN LARP
@bot.command(description="Kiss someone.")
async def kiss(ctx, user: discord.Member):
    embed = funcs.create_embed(
        ctx, f"{ctx.author.mention} kisses {user.mention}!")
    choice = f"kiss{random.randint(1, 2)}.gif"
    file = discord.File(f"pics/{choice}")
    embed.set_image(url=f"attachment://{choice}")
    await ctx.respond(embed=embed, file=file)

@bot.command(description="Hug someone.")
async def hug(ctx, user: discord.Member):
    embed = funcs.create_embed(
        ctx, f"{ctx.author.mention} hugs {user.mention}!")
    file = discord.File("pics/hug1.gif")
    embed.set_image(url=f"attachment://hug1.gif")
    await ctx.respond(embed=embed, file=file)

@bot.command(description="Slap someone.")
async def slap(ctx, user: discord.Member):
    embed = funcs.create_embed(ctx, f"{ctx.author.mention} slaps {user.mention}!")
    file = discord.File("pics/slap1.gif")
    embed.set_image(url=f"attachment://slap1.gif")
    await ctx.respond(embed=embed, file=file)

@bot.command(description="Involuntarily plasure someone.")
async def rape(ctx, user: discord.Member):
    embed = funcs.create_embed(
        ctx, f"{ctx.author.mention} rapes {user.mention}!")
    choice = f"rape{random.randint(1, 3)}.gif"
    file = discord.File(f"pics/{choice}")
    embed.set_image(url=f"attachment://{choice}")
    await ctx.respond(embed=embed, file=file)

@bot.command(description="Provide a copy of your DNA to someone.")
async def coom(ctx, user: discord.Member):
    embed = funcs.create_embed(
        ctx, f"{ctx.author.mention} cooms on {user.mention}!")
    choice = f"coom{random.randint(1, 1)}.gif"
    file = discord.File(f"pics/{choice}")
    embed.set_image(url=f"attachment://{choice}")
    await ctx.respond(embed=embed, file=file)

# SF SPECIFIC
@bot.command(description='Propose a motion to the senate.', guild_ids=[687732235604066366, 717329133960560662])
async def vote(ctx, motion: discord.Option(str, required=True, choices=["Other", "Mute / Unmute", "Camp / Uncamp", "Kick", "Ban", "Add / Remove senator", "Help / List Senators"]), user: discord.Option(discord.Member, required=False, default="")):
    if(ctx.channel.id != config.senate_channel):
        embed = funcs.create_embed(ctx, ":x: This command is only available in the senate.")
        await ctx.respond(embed=embed)
        return

    isSenator = False
    for role in ctx.author.roles:
        if(role.id == config.senator_role):
            isSenator = True
    if(isSenator == False):
        embed = funcs.create_embed(ctx, f":x: Only senators may start votes.")
        await ctx.respond(embed=embed)
        return

    senators = []
    for member in ctx.guild.members:
        for role in member.roles:
            if(role.id == config.senator_role):
                senators.append(member.id)
    
    if(len(senators) < 3):
        embed = funcs.create_embed(ctx, f":x: There is less than 3 senators.")
        await ctx.respond(embed=embed)
        return

    if(senate.vote_active):
        embed = funcs.create_embed(ctx, f"Please wait for the current motion to finish.")
        await ctx.respond(embed=embed)
        return

    if(motion == "Help / List Senators"):
        text = "The motion ends after the timer reaches 0, or after a majority is decided and the timer reaches halfway."
        text += f"\n\nThere are {len(senators)} senators:\n"
        for senator in senators:
            text += f"<@!{senator}>\n"
        embed = funcs.create_embed(ctx, text)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    if(motion == "Other"):
        await ctx.send_modal(visuals.senateVoteDialog(ctx))
    else:
        if(user == ""):
            embed = funcs.create_embed(ctx, f":x: You must specify a user for this type of vote.")
            await ctx.respond(embed=embed)
            return
        await ctx.defer()
        await funcs.hold_vote(ctx, motion, user)
    return

@bot.command(description="Announce a game.", guild_ids=[687732235604066366, 717329133960560662])
async def host(ctx):
    canHost = False
    for role in ctx.author.roles:
        if(role.id == 772182443247009792):
            canHost = True
    if(canHost):
        cmd = []
        await ctx.channel.send(view=visuals.createGameButton(ctx, cmd, client))
    else:
        embed = funcs.create_embed(ctx, ":x: Certified hosts only")
        await ctx.channel.send(embed=embed)

@bot.command(description="Get info on your sentence.", guild_ids=[687732235604066366, 717329133960560662])
async def camp(ctx):
    isCamped = False
    for role in ctx.author.roles:
        if(role.id == 835573253858263050):
            isCamped = True
            if(funcs.sdb.get_value(ctx.author.id, "campAmount") < 1):
                funcs.sdb.set_value(ctx.author.id, "campAmount", 20)

    if(isCamped == False):
        embed = funcs.create_embed(ctx, f":x: You are not camped.")
        await ctx.respond(embed=embed)
        if(funcs.sdb.get_value(ctx.author.id, "campAmount") > 0):
            funcs.sdb.set_value(ctx.author.id, "campAmount", 0)
        return

    info = "You are in the camp. In order to leave, you must work to pay your debts to society. "
    info += f"Use `/mine` to begin your journey."
    info += f"\n\n{funcs.sdb.get_value(ctx.author.id, 'campAmount')} rocks :rock: left."
    embed = funcs.create_embed(ctx, info)
    await ctx.respond(embed=embed)
    return

@bot.command(description='Work your way out of the camp.', guild_ids=[687732235604066366, 717329133960560662])
async def mine(ctx):
    isCamped = False
    for role in ctx.author.roles:
        if(role.id == 835573253858263050):
            isCamped = True
            if(funcs.sdb.get_value(ctx.author.id, "campAmount") < 1):
                funcs.sdb.set_value(ctx.author.id, "campAmount", 20)

    if(isCamped == False):
        embed = funcs.create_embed(ctx, f":x: You are not camped.")
        await ctx.respond(embed=embed)
        if(funcs.sdb.get_value(ctx.author.id, "campAmount") > 0):
            funcs.sdb.set_value(ctx.author.id, "campAmount", 0)
        return

    if(funcs.sdb.get_value(ctx.author.id, "campCooldown") > int(time.time())):
        embed = funcs.create_embed(
            ctx, f"You need to rest for {funcs.sdb.get_value(ctx.author.id, 'campCooldown') - int(time.time())} more seconds.")
        await ctx.respond(embed=embed)
        return

    phrases = [":pick: You slave away.",
               ":pick: You keep mining.", ":pick: You start sweating."]

    funcs.sdb.set_value(ctx.author.id, "campAmount",
                  funcs.sdb.get_value(ctx.author.id, "campAmount") - 1)

    if(funcs.sdb.get_value(ctx.author.id, "campAmount") == 0):
        role = get(ctx.author.guild.roles, id=835573253858263050)
        await ctx.author.remove_roles(role)
        embed = funcs.create_embed(ctx, f"You are finally free.")
        await ctx.respond(embed=embed)
        return

    funcs.sdb.set_value(ctx.author.id, "campCooldown", int(time.time() + 3))

    embed = funcs.create_embed(ctx, random.choice(
        phrases), footer=f"{funcs.sdb.get_value(ctx.author.id, 'campAmount')} rocks left.")
    await ctx.respond(embed=embed)

@bot.command(description='StormNet server and service status.', guild_ids=[687732235604066366, 717329133960560662])
async def service(ctx):
    services = {"mc": True, "stormbot": False, "agencybot": False, "slurbot": False, "schizobot": False, "unturned": False, "zerotier-one": False}
    desc = ""

    for service in services:
        if(os.system(f"service {service} status") == 0):
            desc+=f":green_circle: `{service}` **RUNNING**\n"
        else:
            desc+=f":red_circle: `{service}` **STOPPED**\n"
    
    embed = funcs.create_embed(ctx, desc, "StormNet Service Status")
    await ctx.respond(embed=embed, view=visuals.createServiceButtons(ctx, services))

# EVENTS
@bot.event
async def on_message(ctx):
    if(ctx.author.bot): return

    if(ctx.guild.id == 687732235604066366):
        if(random.randint(1, 200) == 1):
            prize = random.choice([100, 250, 500, 1000])
            funcs.sdb.add_credits(ctx.author.id, prize)
            embed = funcs.create_embed(ctx, f"RNG gave {ctx.author.mention} {prize} credits for free. Go gamble it away.")
            await ctx.channel.send(embed=embed, view=visuals.createSpendingButton(ctx))

    if(ctx.guild.id == 717329133960560662):
        prize = random.choice([100, 250, 500, 1000])
        funcs.sdb.add_credits(ctx.author.id, prize)
        embed = funcs.create_embed(ctx, f"RNG gave {ctx.author.mention} {prize} credits for free. Go gamble it away.")
        await ctx.channel.send(embed=embed, view=visuals.createSpendingButton(ctx))

bot.run(config.token)
