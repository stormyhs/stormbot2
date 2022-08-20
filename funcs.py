import asyncio
import discord
import random
import datetime

import dbhandler
import config
import visuals
import senate

sdb = dbhandler.db_handler()

def create_account_if_not_exist(ctx):
    sdb.create_account(ctx.author.id)

def setfootertext(ctx):
    dt = datetime.datetime.now()
    text = f"{ctx.author.name} • {dt.strftime('%H')}:{dt.strftime('%M')}"
    return text

def dotnumbers(number):
    new_number = "{:,}".format(number)
    return new_number.replace(",", ".")

def create_embed(ctx, desc, title="", footer=""):
    embed = discord.Embed(title=title, description=desc)
    if(footer == ""):
        embed.set_footer(text=setfootertext(ctx))
    else:
        embed.set_footer(text=footer)
    return embed

async def presentBlackjackOptions(ctx):
    await ctx.channel.send("Place your bet, and count some cards!", view=visuals.createBlackjackButton(ctx))

async def presentSlotsOptions(ctx):
    await ctx.channel.send("Place your bet, and spin!", view=visuals.createSlotsButton(ctx))

async def generate_slot_icon_bar(winning=False):
    icons = [":potato:", ":roll_of_paper:", ":carrot:", ":game_die:", ":strawberry:", ":pizza:"]
    good_icons = [":seven:", ":pizza:"]
    
    bar = random.choice(icons) + random.choice(icons) + random.choice(icons) + "\n"
    if(winning):
        bar += random.choice(good_icons) * 3
    else:
        bar += random.choice(icons) * 3
    bar += "\n" + random.choice(icons) + random.choice(icons) + random.choice(icons) + "\n"
    
    return bar

async def slots(ctx, amount):
    print(amount)
    if(amount < 25):
        embed = create_embed(ctx, f":x: Please enter at least 25 credits.")
        await ctx.respond(embed=embed)
        return

    if(sdb.get_value(ctx.author.id, "credits") < amount):
        embed = create_embed(ctx, f":x: You do not have {amount} credits.")
        await ctx.respond(embed=embed)
        return

    sdb.add_credits(ctx.author.id, -amount)
    prize = 0

    embed = create_embed(ctx, f"You spin the slots...")
    try:
        msg = await ctx.respond(embed=embed)
    except:
        msg = await ctx.channel.send(embed=embed)

    await asyncio.sleep(2.5)

    n = random.randint(1, 100)
    prize = 0

    winning = True
    if(n <= 2):
        prize = amount * 10
        title = "JACKPOT!"
    elif(n <= 12):
        prize = amount * 7
        title = "You've hit a fortune!"
    elif(n <= 34):
        prize = amount * 3
        title = "You beat the slots!"
    elif(n <= 60):
        title = "You won a small prize."
        prize = (amount * 2) + random.randint(50, 250)
    else:
        winning = False
        title = random.choice(["No luck this time.", "Bad spin this round."])
    
    if(prize > 0):
        sdb.add_credits(ctx.author.id, prize)
    
    slot_icons = await generate_slot_icon_bar(winning)
    embed = create_embed(ctx, slot_icons)
    embed.add_field(name=title, value=f"Your prize: **◈{prize}**\nYour balance: {sdb.cool_balance(ctx.author.id)}")
    try:
        await msg.edit(embed=embed, view=visuals.createSlotsButton(ctx))
    except:    
        await msg.edit_original_message(embed=embed, view=visuals.createSlotsButton(ctx))

async def shop(ctx):
    embed = create_embed(ctx, f"Select any item below to purchase.\nYour current balance is {sdb.cool_balance(ctx.author.id)}.", f":shopping_cart: The Shop")
    await ctx.channel.send(embed=embed, view=visuals.createShopButton(ctx))

async def rp(ctx, cmd):
    if(len(ctx.mentions) < 1):
        return

    if(cmd[0] == "kiss"):
        embed = create_embed(
            ctx, f"{ctx.author.mention} kisses {ctx.mentions[0].mention}!")
        choice = f"kiss{random.randint(1, 2)}.gif"
        file = discord.File(f"pics/{choice}")
        embed.set_image(url=f"attachment://{choice}")
        await ctx.channel.send(embed=embed, file=file)
    elif(cmd[0] == "hug"):
        embed = create_embed(
            ctx, f"{ctx.author.mention} hugs {ctx.mentions[0].mention}!")
        file = discord.File("pics/hug1.gif")
        embed.set_image(url=f"attachment://hug1.gif")
        await ctx.channel.send(embed=embed, file=file)
    elif(cmd[0] == "slap"):
        embed = create_embed(
            ctx, f"{ctx.author.mention} slaps {ctx.mentions[0].mention}!")
        file = discord.File("pics/slap1.gif")
        embed.set_image(url=f"attachment://slap1.gif")
        await ctx.channel.send(embed=embed, file=file)
    elif(cmd[0] == "rape"):
        embed = create_embed(
            ctx, f"{ctx.author.mention} rapes {ctx.mentions[0].mention}!")
        choice = f"rape{random.randint(1, 3)}.gif"
        file = discord.File(f"pics/{choice}")
        embed.set_image(url=f"attachment://{choice}")
        await ctx.channel.send(embed=embed, file=file)
    elif(cmd[0] == "coom"):
        embed = create_embed(
            ctx, f"{ctx.author.mention} cooms on {ctx.mentions[0].mention}!")
        choice = f"coom{random.randint(1, 1)}.gif"
        file = discord.File(f"pics/{choice}")
        embed.set_image(url=f"attachment://{choice}")
        await ctx.channel.send(embed=embed, file=file)

async def blackjack(message, amount):
    # WARNING: hazardous code ahead
    # Don't care enough to rewrite it
    
    if(str(message.author.id) in senate.blackjack):
        embed = discord.Embed(
            description=":x: Already playing a blackjack game.")
        embed.set_footer(text=setfootertext(message))
        await message.respond(embed=embed)
        return

    if(sdb.get_value(message.author.id, "credits") < amount):
        embed = create_embed(message, f":x: You do not have enough credits.")
        await message.respond(embed=embed)
        return

    if(amount < 25):
        embed = discord.Embed(description=":x: Please enter at least 25 credits.")
        embed.set_footer(text=setfootertext(message))
        await message.respond(embed=embed)
        return

    senate.blackjack[str(message.author.id)] = None
    deck = []
    vals = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'K', 'Q', 'J', 'A']
    suits = ['S', 'C', 'H', 'D']
    for suit in suits:
        for val in vals:
            deck.append("{}{}".format(suit, val))
    random.shuffle(deck)
    print(deck)
    gameActive = True
    tie1 = False
    tie2 = False
    won1 = False
    won2 = False
    playerHand = []
    playerHand2 = []
    dealerHand = []
    embed = discord.Embed(title="Blackjack")
    i = 0
    bonus1 = ""
    bonus2 = ""
    canSplit = False
    hasSplit = False
    activeHand = 2  # changes to 1 on start
    hand1active = True
    hand2active = False
    timeToEnd = 150
    while(gameActive == True):
        if(i == 0):
            chosen = random.choice(deck)
            playerHand.append(chosen)
            deck.remove(chosen)
            chosen = random.choice(deck)
            dealerHand.append(chosen)
            deck.remove(chosen)
            chosen = random.choice(deck)
            playerHand.append(chosen)
            deck.remove(chosen)
            if(handValue([playerHand[0]]) == handValue([playerHand[1]])):
                if(sdb.get_value(message.author.id, "credits") >= amount * 2):
                    canSplit = True
        else:
            userActed = False
            while(userActed == False):
                if(senate.blackjack[str(message.author.id)] == "👋"):
                    userActed = True
                    senate.blackjack[str(message.author.id)] = None
                    chosen = random.choice(deck)
                    if(activeHand == 1):
                        playerHand.append(chosen)
                    else:
                        playerHand2.append(chosen)
                    deck.remove(chosen)
                elif(senate.blackjack[str(message.author.id)] == "✋"):
                    userActed = True
                    senate.blackjack[str(message.author.id)] = None
                elif(senate.blackjack[str(message.author.id)] == "✌️"):
                    if(hasSplit == False and canSplit == True):
                        userActed = True
                        senate.blackjack[str(message.author.id)] = None
                        hasSplit = True
                        canSplit = False
                        hand2active = True
                        playerHand2.append(playerHand[1])
                        playerHand.pop(1)
                    else:
                        senate.blackjack[str(message.author.id)] = None
                elif(senate.blackjack[str(message.author.id)] == "✌️"):
                    userActed = True
                    senate.blackjack[str(message.author.id)] = None
                    await cmsg.delete()
                    embed = discord.Embed(title="Blackjack")
                    embed.add_field(name="{}'s hand".format(message.author.name), value="{}\nValue: {}".format(
                        playerHandDisplay, handValue(playerHand)))
                    embed.add_field(
                        name="Blackjack Table", value="**◈{}** prize pool.\n{}".format(amount, bonus1))
                    embed.add_field(name="Dealer's hand", value="{}\nValue: {}".format(
                        dealerHandDisplay, handValue(dealerHand)))
                    embed.add_field(name=":x: {} has forefit the game.".format(
                        message.author.name), value="**◈{}** lost.".format(amount))
                    await message.respond(embed=embed)
                    sdb.add_credits(
                        message.author.id, -amount)
                    del senate.blackjack[str(message.author.id)]
                    return

                canSplit = False
                if(userActed == False):
                    await asyncio.sleep(1)
                    timeToEnd -= 1
                    if(timeToEnd <= 0):
                        embed = discord.Embed(title="Blackjack")
                        embed.add_field(name="{}'s hand".format(message.author.name), value="{}\nValue: {}".format(
                            playerHandDisplay, handValue(playerHand)))
                        embed.add_field(
                            name="Blackjack Table", value="**◈{}** prize pool.\n{}".format(amount, bonus1))
                        embed.add_field(name="Dealer's hand", value="{}\nValue: {}".format(
                            dealerHandDisplay, handValue(dealerHand)))
                        embed.add_field(name=":x: {} has forefit the game (timeout).".format(
                            message.author.name), value="**◈{}** lost.".format(amount))
                        await cmsg.edit_original_message(embed=embed)
                        sdb.add_credits(message.author.id, -amount)
                        del senate.blackjack[str(message.author.id)]
                        return
        if(i != 0):
            if not (hasSplit == True and i == 1):
                if(handValue(dealerHand) < 17):
                    while(handValue(dealerHand) < 17):
                        chosen = random.choice(deck)
                        dealerHand.append(chosen)
                        deck.remove(chosen)
                        print(handValue(dealerHand))

        if(activeHand == 2):
            if(hand1active == True):
                activeHand = 1
        else:
            if(hand2active == True):
                activeHand = 2

        playerHandDisplay = ""
        for card in playerHand:
            playerHandDisplay = playerHandDisplay + cardText(card)
        playerHandDisplay2 = ""
        for card in playerHand2:
            playerHandDisplay2 = playerHandDisplay2 + cardText(card)
        dealerHandDisplay = ""
        for card in dealerHand:
            dealerHandDisplay = dealerHandDisplay + cardText(card)

        embed = discord.Embed(title="Blackjack")

        if(activeHand == 1):
            embed.add_field(name=">>{}'s hand<<".format(message.author.name),
                            value="{}\nValue: {}".format(playerHandDisplay, handValue(playerHand)))
        else:
            embed.add_field(name="{}'s hand".format(message.author.name), value="{}\nValue: {}".format(
                playerHandDisplay, handValue(playerHand)))
        if(hasSplit == True):
            if(activeHand == 2):
                embed.add_field(name=">>{}'s hand<<".format(message.author.name), value="{}\nValue: {}".format(
                    playerHandDisplay2, handValue(playerHand2)))
            else:
                embed.add_field(name="{}'s hand".format(message.author.name), value="{}\nValue: {}".format(
                    playerHandDisplay2, handValue(playerHand2)))
        else:
            embed.add_field(
                name="Blackjack Table", value="**◈{}** prize pool.\n{}".format(amount, bonus1))
        embed.add_field(name="Dealer's hand", value="{}\nValue: {}".format(
            dealerHandDisplay, handValue(dealerHand)))
        if(handValue(playerHand) == 21):
            bonus1 = "\n:fire: **50% 21 BONUS** :fire:"
            if(bonus1 != ""):
                embed.add_field(name="{} won!".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
            else:
                embed.add_field(name="{} won!".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
            hand1active = False
            won1 = True
        elif(handValue(dealerHand) == 21):
            embed.add_field(name="{} lost.".format(
                message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") - amount), inline=True)
            hand1active = False
            won1 = False
        elif(handValue(playerHand) > 21):
            embed.add_field(name="{} lost.".format(
                message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") - amount), inline=True)
            hand1active = False
            won1 = False
        elif(handValue(dealerHand) > 21):
            if(bonus1 != ""):
                embed.add_field(name="{} won!".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
            else:
                embed.add_field(name="{} won!".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
            hand1active = False
            won1 = True
        elif(handValue(dealerHand) >= 17):
            if(handValue(playerHand) > handValue(dealerHand)):
                if(bonus1 != ""):
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
                else:
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
                hand1active = False
                won1 = True
            elif(handValue(playerHand) == handValue(dealerHand)):
                embed.add_field(
                    name="Push!", value="**◈{}** refunded.".format(amount), inline=True)
                hand1active = False
                won1 = False
                tie1 = True
        if(hasSplit == True):
            if(handValue(playerHand2) == 21):
                bonus2 = "\n:fire: **50% BONUS** :fire:"
                if(bonus2 != ""):
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
                else:
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
                hand2active = False
                won2 = True
            elif(handValue(dealerHand) == 21):
                embed.add_field(name="{} lost.".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") - amount), inline=True)
                hand2active = False
                won2 = False
            elif(handValue(playerHand2) > 21):
                embed.add_field(name="{} lost.".format(
                    message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") - amount), inline=True)
                hand2active = False
                won2 = False
            elif(handValue(dealerHand) > 21):
                if(bonus2 != ""):
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
                else:
                    embed.add_field(name="{} won!".format(
                        message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
                hand2active = False
                won2 = True
            elif(handValue(dealerHand) >= 17):
                if(handValue(playerHand2) > handValue(dealerHand)):
                    if(bonus2 != ""):
                        embed.add_field(name="{} won!".format(
                            message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + int(amount * 1.5)), inline=True)
                    else:
                        embed.add_field(name="{} won!".format(
                            message.author.name), value="Balance: **◈{}**.".format(sdb.get_value(message.author.id, "credits") + amount), inline=True)
                    hand2active = False
                    won2 = True
                elif(handValue(playerHand2) == handValue(dealerHand)):
                    embed.add_field(name=message.author.name, value="Balance: **◈{}**. Your credits have been refunded.".format(
                        sdb.get_value(message.author.id, "credits")), inline=True)
                    hand2active = False
                    won2 = False
                    tie2 = True

        if(hand1active == False and hand2active == False):
            gameActive = False

        if(i > 0):
            if(gameActive):
                try:
                    await cmsg.edit_original_message(embed=embed)
                except:
                    await cmsg.edit(embed=embed)
        
        else:
            try:
                cmsg = await message.respond(embed=embed, view=visuals.createBlackjackIngameButtons(message, canSplit))
            except:
                cmsg = await message.channel.send(embed=embed, view=visuals.createBlackjackIngameButtons(message, canSplit))
        
        await asyncio.sleep(2)
        i = i + 1

    del senate.blackjack[str(message.author.id)]

    if(won1 == True):
        if(bonus1 != ""):
            sdb.add_credits(message.author.id, int(amount * 1.5))
        else:
            sdb.add_credits(message.author.id, amount)
    else:
        if(tie1 == True):
            pass
        else:
            sdb.add_credits(message.author.id, -amount)

    if(hasSplit == True):
        if(won2 == True):
            if(bonus2 != ""):
                sdb.add_credits(message.author.id, int(amount * 1.5))
            else:
                sdb.add_credits(message.author.id, amount)
        else:
            if(tie2 == True):
                pass
            else:
                sdb.add_credits(message.author.id, -amount)
    
    print(dir(cmsg))
    try:
        await cmsg.edit_original_message(embed=embed, view=visuals.createBlackjackButton(message))
    except:
        try:
            await cmsg.edit(embed=embed, view=visuals.createBlackjackButton(message)) #TODO: smth dying here
        except:
            await message.channel.send(embed=embed, view=visuals.createBlackjackButton(message))

def cardText(chosen):
    suit = ""
    chosen = str(chosen)
    if(chosen[0] == "S"):
        suit = " of Spades"
        suit = ":spades:"
    if(chosen[0] == "C"):
        suit = " of Clubs"
        suit = ":clubs:"
    if(chosen[0] == "H"):
        suit = " of Hearts"
        suit = ":hearts:"
    if(chosen[0] == "D"):
        suit = " of Diamonds"
        suit = ":diamonds:"
    try:
        value = int(chosen[1])
        if(value == 1):
            value = 10
    except:
        if(chosen[1] == "K"):
            value = "K"
        if(chosen[1] == "Q"):
            value = "Q"
        if(chosen[1] == "J"):
            value = "J"
        if(chosen[1] == "A"):
            value = "A"
    cardtext = suit + str(value)
    return cardtext

def handValue(hand):
    value = 0
    for card in hand:
        try:
            if(int(card[1]) == 1):
                value = value + 10
            else:
                value = value + int(card[1])
        except:
            if(card[1] == "A"):
                value = value + 11
            else:
                value = value + 10
    for card in hand:
        if(card[1] == "A"):
            if(value > 21):
                value = value - 10
    return value

async def kick(ctx, user):
    desc = f"You have been kicked from **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")
    try:
        await user.kick()
        await ctx.send(f"Kicked {user.mention}.")
    except:
        await ctx.send(":x: Was not able to kick.")

async def ban(ctx, user):
    desc = f"You have been banned from **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")
    try:
        await user.ban(delete_message_days=0)
        await ctx.send(f"Banned {user.mention}.")
    except:
        await ctx.send(":x: Was not able to ban.")

async def mute(ctx, user):
    desc = f"You have been muted in **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=741708944296378482)
        await user.add_roles(mute)
        await ctx.send(f"{user.mention} has been muted.")
    except:
        await ctx.send(":x: Could not assign role.")

async def unmute(ctx, user):
    desc = f"You have been unmuted in **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=741708944296378482)
        await user.remove_roles(mute)
        await ctx.send(f"{user.mention} has been unmuted.")
    except:
        await ctx.send(":x: Could not remove role.")

async def camp(ctx, user):
    desc = f"You have been camped in **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    desc += f"\nUse `/camp` for info."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=835573253858263050)
        await user.add_roles(mute)
        await ctx.send(f"{user.mention} has been camped.")
    except Exception as e:
        print(e)
        print(dir(user))
        await ctx.send(":x: Could not assign role.")

async def uncamp(ctx, user):
    desc = f"You have been uncamped in **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=835573253858263050)
        await user.remove_roles(mute)
        await ctx.send(f"{user.mention} has been uncamped.")
    except:
        await ctx.send(":x: Could not remove role.")

async def addsenator(ctx, user):
    desc = f"You have been added to the senate of **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=748740175450079273)
        await user.add_roles(mute)
        await ctx.send(f"{user.mention} has been added as a senator.")
    except:
        await ctx.send(":x: Could not assign role.")

async def removesenator(ctx, user):
    desc = f"You have been removed from the senate of **{ctx.guild.name}** by **{ctx.author.name}**"
    desc += f"\nReason: Senate vote."
    embed = discord.Embed(description=desc)

    try:
        userdm = await user.create_dm()
        await userdm.send(embed=embed)
    except:
        await ctx.send(":x: Was not able to send DM.")

    try:
        mute = discord.utils.get(ctx.guild.roles, id=748740175450079273)
        await user.remove_roles(mute)
        await ctx.send(f"{user.mention} has been removed from the senate.")
    except:
        await ctx.send(":x: Could not remove role.")
