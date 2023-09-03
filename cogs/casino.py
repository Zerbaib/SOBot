import datetime
import json
import random
import time

import disnake
from disnake.ext import commands

from utils import error, var



cooldown_time = var.cooldown_time

class CasinoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = var.economy_data_file_path
        self.cooldown_file = var.casino_cooldown_data_file_path
        self.min_balance = 50
        self.server_data = {}

    def load_data(self, server_id):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                return data.get(server_id, {})
        except FileNotFoundError:
            return {}

    def save_data(self, server_id, data):
        with open(self.data_file, 'r') as file:
            all_data = json.load(file)
            all_data[server_id] = data

        with open(self.data_file, 'w') as file:
            json.dump(all_data, file, indent=4)

    def load_cooldown(self, server_id):
        try:
            with open(self.cooldown_file, 'r') as file:
                cooldown_data = json.load(file)
                return cooldown_data.get(server_id, {})
        except FileNotFoundError:
            return {}

    def save_cooldown(self, server_id, cooldown_data):
        with open(self.cooldown_file, 'r') as file:
            all_cooldown_data = json.load(file)
            all_cooldown_data[server_id] = cooldown_data

        with open(self.cooldown_file, 'w') as file:
            json.dump(all_cooldown_data, file, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        print('========== ⚙️ Casino ⚙️ ==========')
        print('🔩 /earn has been loaded')
        print('🔩 /bet has been loaded')
        print('🔩 /dice has been loaded')
        print('🔩 /caster has been loaded')
        print('🔩 /slot has been loaded')
        print()

    @commands.slash_command(name="earn", description="Earn coins")
    async def earn(self, ctx):
        try:
            server_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)
            current_time = int(datetime.datetime.now().timestamp())
            data = self.load_data(server_id)
            data_c = self.load_cooldown(server_id)

            last_earn_time = data_c.get(user_id, 0)

            if current_time - last_earn_time >= 7200:
                data.setdefault(user_id, 0)
                earnings = data[user_id] + 100
                data[user_id] = earnings
                data_c[user_id] = current_time
                self.save_data(server_id, data)
                self.save_cooldown(server_id, data_c)

                embed = disnake.Embed(
                    title="💸 Earn Coins 💸",
                    description=f"You earned 100 coins 🪙!\nYour total balance: ``{earnings}`` coins.",
                    color=disnake.Color.green()
                )
                await ctx.response.defer()
                await ctx.send(embed=embed)
            else:
                remaining_time = 7200 - (current_time - last_earn_time)
                remaining_time_str = str(datetime.timedelta(seconds=remaining_time))

                embed = disnake.Embed(
                    title="🕰 Earn Coins 🕰",
                    description=f"You are on cooldown.\nTry again in ``{remaining_time_str}`` ⏳.",
                    color=disnake.Color.red()
                )
                await ctx.response.defer()
                await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="bet", description="Bet coins | x2 or lost")
    async def bet(self, ctx, amount: int):
        try:
            server_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)
            data = self.load_data(server_id)

            if amount <= 0 or user_id not in data or data[user_id] < amount:
                embed = disnake.Embed(
                    title="Invalid Bet",
                    description="Invalid bet amount or insufficient balance.",
                    color=disnake.Color.red()
                )
                await ctx.response.send_message(embed=embed)
                return

            win_chance = 25
            outcome = random.choices([True, False], weights=[win_chance, 100 - win_chance], k=1)[0]

            if outcome:
                winnings = amount * 2
                data[user_id] += winnings
                embed = disnake.Embed(
                    title="💰 You Won!",
                    description=f"Congratulations! You won the bet.\nYou earned `{winnings}` coins!",
                    color=disnake.Color.green()
                )
            else:
                data[user_id] -= amount
                embed = disnake.Embed(
                    title="😢 You Lost",
                    description=f"Better luck next time. You lost `{amount}` coins.",
                    color=disnake.Color.red()
                )

            self.save_data(server_id, data)

            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="dice", description="Play the dice game")
    async def dice(self, ctx, bet: int):
        try:
            server_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)
            data = self.load_data(server_id)

            if bet <= 0 or user_id not in data or data[user_id] < bet:
                embed = disnake.Embed(
                    title="Invalid Bet",
                    description="Invalid bet amount or insufficient balance.",
                    color=disnake.Color.red()
                )
                await ctx.response.send_message(embed=embed)
                return
            dice_result = random.randint(1, 6)

            if dice_result == 1:
                data[user_id] -= bet
                embed = disnake.Embed(
                    title="🎲 Dice Game",
                    description=f"Sorry, you rolled a 1 and lost `{bet}` coins.",
                    color=disnake.Color.red()
                )
            else:
                winnings = bet * dice_result
                data[user_id] += winnings
                embed = disnake.Embed(
                    title="🎲 Dice Game",
                    description=f"Congratulations! You rolled a `{dice_result}` and won `{winnings}` coins!",
                    color=disnake.Color.green()
                )

            self.save_data(server_id, data)

            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="caster", description="Play a game of caster")
    async def caster(self, ctx, bet_option: str, bet_amount: int):
        try:
            server_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)
            data = self.load_data(server_id)

            if bet_option not in ("red", "black", "even", "odd") or bet_amount <= 0 or user_id not in data or data[user_id] < bet_amount:
                embed = disnake.Embed(
                    title="Invalid Bet",
                    description="Invalid bet option, amount, or insufficient balance.",
                    color=disnake.Color.red()
                )
                await ctx.response.send_message(embed=embed)
                return

            result = random.choice(["red", "black", "even", "odd"])
            payout = 2

            if bet_option == result:
                winnings = bet_amount * payout
                data[user_id] += winnings
                embed = disnake.Embed(
                    title="Caster Game",
                    description=f"Congratulations! The caster rolled `{result}`.\nYou won `{winnings}` coins!",
                    color=disnake.Color.green()
                )
            else:
                data[user_id] -= bet_amount
                embed = disnake.Embed(
                    title="Caster Game",
                    description=f"Sorry, the caster rolled `{result}` and you lost `{bet_amount}` coins.",
                    color=disnake.Color.red()
                )

            self.save_data(server_id, data)

            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name='slot', description='Play the slot machine')
    async def slot(self, ctx, bet: int):
        try:
            server_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)
            data = self.load_data(server_id)

            if bet <= 0 or user_id not in data or data[user_id] < bet:
                embed = disnake.Embed(
                    title="Invalid Bet",
                    description="Invalid bet amount or insufficient balance.",
                    color=disnake.Color.red()
                )
                await ctx.response.send_message(embed=embed)
                return

            reels = var.slot_emoji
            result = [random.choice(reels) for _ in range(3)]

            if result[0] == result[1] == result[2]:
                winnings = bet * 10
                data[user_id] += winnings
                embed = disnake.Embed(
                    title="🎰 Slot Machine",
                    description=f"Congratulations! You got `{result[0]}` `{result[1]}` `{result[2]}`.\nYou won `{winnings}` coins!",
                    color=disnake.Color.green()
                )
            else:
                data[user_id] -= bet
                embed = disnake.Embed(
                    title="🎰 Slot Machine",
                    description=f"Sorry, you got `{result[0]}` `{result[1]}` `{result[2]}` and lost `{bet}` coins.",
                    color=disnake.Color.red()
                )

            self.save_data(server_id, data)

            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CasinoCommands(bot))
