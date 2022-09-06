import os
import discord
import funcs
import senate
import config

def createSpendingButton(ctx):
    class spendingButtons(discord.ui.View):
        @discord.ui.select(
            placeholder="Make it disappear?",
            options = [
                discord.SelectOption(label="🎰 Spin the slots", value="slots"),
                discord.SelectOption(label="🃏 Play some blackjack", value="blackjack"),
                discord.SelectOption(label="🛒 Go shopping", value="shop")
                ]
        )
        async def select_game(self, select, interaction): # the function called when the user is done selecting options
            if(ctx.author.id == interaction.user.id):
                if(select.values[0] == "slots"):
                    await interaction.response.defer()
                    await funcs.presentSlotsOptions(ctx)
                elif(select.values[0] == "blackjack"):
                    await interaction.response.defer()
                    await funcs.presentBlackjackOptions(ctx)
                elif(select.values[0] == "shop"):
                    await interaction.response.defer()
                    await funcs.shop(ctx)
    return spendingButtons()

def createSlotsButton(ctx):
    class slotsButtons(discord.ui.View):
        choices = []
        all = funcs.sdb.get_value(ctx.author.id, "credits")
        choices.append(discord.SelectOption(label=f"All in ({all})", value=all))
        for n in [25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 15000, 20000]:
            choices.append(discord.SelectOption(label=f"Bet {n} credits", value=n))

        @discord.ui.select(
            placeholder = "Bet again?",
            options = choices
        )

        async def callback(self, button, interaction):
            if(interaction.user.id == ctx.author.id):
                await interaction.response.defer()
                await ctx.channel.send(f"Betting {button.values[0]}")
                await funcs.slots(ctx, int(button.values[0]))
    return slotsButtons()

def createBlackjackButton(ctx):
    class blackjackButtons(discord.ui.View):
        choices = []
        all = funcs.sdb.get_value(ctx.author.id, "credits")
        choices.append(discord.SelectOption(label=f"All in ({all})", value=all))
        for n in [25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 15000, 20000]:
            choices.append(discord.SelectOption(label=f"Bet {n} credits", value=n))    

        @discord.ui.select(
            placeholder = "Bet again?",
            options = choices
        )

        async def callback(self, button, interaction):
            if(interaction.user.id == ctx.author.id):
                await interaction.response.defer()
                await ctx.channel.send(f"Betting {button.values[0]}")
                await funcs.blackjack(ctx, int(button.values[0]))

    return blackjackButtons()

class senateVotes(discord.ui.View):
    @discord.ui.select(
        placeholder = "Select your vote.",
        options = [
            discord.SelectOption(label=f"Approve.", value=2, emoji="👍"),
            discord.SelectOption(label=f"Abstain.", value=1, emoji="🤐"),
            discord.SelectOption(label=f"Disapprove.", value=3, emoji="👎")
        ]
    )
    async def callback(self, button, interaction):
        await interaction.response.defer()
        canVote = False
        for role in interaction.user.roles:
            if(role.id == config.senator_role):
                canVote = True
                break
        # i dont care
        if(canVote):
            if(interaction.user.id in senate.yes):
                senate.yes.remove(interaction.user.id)
            if(interaction.user.id in senate.no):
                senate.no.remove(interaction.user.id)
            if(interaction.user.id in senate.abstain):
                senate.abstain.remove(interaction.user.id)
            if(int(button.values[0]) == 1):
                senate.abstain.append(interaction.user.id)
            if(int(button.values[0]) == 2):
                senate.yes.append(interaction.user.id)
            if(int(button.values[0]) == 3):
                senate.no.append(interaction.user.id)

def createShopButton(ctx):
    class nicknameModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_item(discord.ui.InputText(label="New nickname:"))

        async def callback(self, interaction: discord.Interaction):
            if(len(self.children[0].value) > 32):
                await interaction.response.send_message(":x: 32 characters maximum.")
                return
            if(funcs.sdb.get_value(ctx.author.id, "credits") < 500):
                await interaction.response.send_message(":x: You do not have enough credits.")
                return
            try:
                await ctx.author.edit(nick=self.children[0].value)
                funcs.sdb.add_credits(ctx.author.id, -500)
                await interaction.response.send_message("Enjoy your new nickname.")
            except Exception as e:
                await interaction.response.send_message(f":x: Error: {e}\n\nBother stormy about it.")

    class shopButton(discord.ui.View):
        @discord.ui.select(
            placeholder = "Pick an item to buy.",
            options = [
                discord.SelectOption(label=f"Not", value=1),
                discord.SelectOption(label=f"Yet", value=2),
                discord.SelectOption(label=f"Ready", value=3)
            ]
        )
        async def callback(self, button, interaction):
            pass

    return shopButton()

def createGameButton(ctx, cmd, client): # TODO clean args
    class MyModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_item(discord.ui.InputText(label="When?"))
            self.add_item(discord.ui.InputText(label="Any mods?"))
            self.add_item(discord.ui.InputText(label="What version?"))

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title=self.title, description=f"Leave a 👍 if you intend to join.")
            embed.add_field(name="TIME", value=self.children[0].value)
            embed.add_field(name="MODS", value=self.children[1].value)
            embed.add_field(name="VERSION", value=self.children[2].value)
            
            channel = client.get_channel(config.game_log)
            if (self.title == "Hearts of Iron IV"):
                role = f"<@&699940660077265008>"
            elif(self.title == "Europa Universalis IV"):
                role = f"<@&698976626729418843>"
            elif(self.title == "Victoria II"):
                role = f"<@&772143066983038996>"
            elif(self.title == "Crusader Kings III"):
                role = f"<@&750695539917586563>"
            msg = await channel.send(role, embed=embed)
            await msg.add_reaction("👍")
            
            await interaction.response.send_message("Game announced.")

    class gameButton(discord.ui.View):
        @discord.ui.select(
            placeholder = "Select a game.",
            options = [
                discord.SelectOption(label=f"Hearts of Iron IV", value=f"Hearts of Iron IV"),
                discord.SelectOption(label=f"Europa Universalis IV", value=f"Europa Universalis IV"),
                discord.SelectOption(label=f"Crusader Kings III", value=f"Crusader Kings III"),
                discord.SelectOption(label=f"Victoria II", value=f"Victoria II")
            ]
        )
        async def callback(self, button, interaction):
            # i dont care
            canHost = False
            for role in interaction.user.roles:
                if(role.id == 772182443247009792):
                    canHost = True
            if(canHost):
                await interaction.response.send_modal(MyModal(title=button.values[0]))
    return gameButton()

def createBlackjackIngameButtons(ctx, canSplit):
    class blackjackIngameButtons(discord.ui.View):
        @discord.ui.button(label="Pull", style=discord.ButtonStyle.primary, emoji="👋")
        async def callback(self, button, interaction):
            if(ctx.author.id == interaction.user.id):
                await interaction.response.defer()
                senate.blackjack[str(interaction.user.id)] = "👋"
        @discord.ui.button(label="Pass", style=discord.ButtonStyle.green, emoji="✋")
        async def callback1(self, button, interaction):
            if(ctx.author.id == interaction.user.id):
                await interaction.response.defer()
                senate.blackjack[str(interaction.user.id)] = "✋"

        if(canSplit):
            @discord.ui.button(label="Split", style=discord.ButtonStyle.green, emoji="✌️")
            async def callback2(self, button, interaction):
                if(ctx.author.id == interaction.user.id):
                    await interaction.response.defer()
                    senate.blackjack[str(interaction.user.id)] = "✌️"

        @discord.ui.button(label="Forefit", style=discord.ButtonStyle.red, emoji="❎")
        async def callback3(self, button, interaction):
            if(ctx.author.id == interaction.user.id):
                await interaction.response.defer()
                senate.blackjack[str(interaction.user.id)] = "❌"
    return blackjackIngameButtons()

def createServiceButtons(ctx, services):
    class serviceButtons(discord.ui.View):
        options = []
        for service in services:
            if(services[service] == True):
                if(os.system(f"service {service} status") != 0):
                    options.append(discord.SelectOption(label=service, value=service))

        @discord.ui.select(
            placeholder = "Select a service to start it.",
            options = options
        )
        async def callback(self, button, interaction):
            if(ctx.author.id == interaction.user.id):
                embed = discord.Embed(description=f"Service is starting. This may take a few minutes.")
                await interaction.response.defer()
                await ctx.channel.send(embed=embed)
                os.system(f"systemctl start {button.values[0]}")
    return serviceButtons()

def senateVoteDialog(ctx):
    class MyModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_item(discord.ui.InputText(label="Motion", style=discord.InputTextStyle.long, placeholder="Write your proposition here."))

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            await funcs.hold_vote(ctx, self.children[0].value)

    return MyModal(title="Propose a motion")
