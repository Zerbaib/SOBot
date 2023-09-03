import disnake
from disnake.ext import commands
import json
from utils import error, var

class EconomyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = var.economy_data_file_path
        self.data = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print('========== ⚙️ Economy ⚙️ ==========')
        print('🔩 /balance has been loaded')
        print('🔩 /baltop has been loaded')
        print('🔩 /pay has been loaded')
        print()

    @commands.slash_command(name="balance", description="Check your balance")
    async def balance(self, ctx):
        try:
            user_id = str(ctx.author.id)
            server_id = str(ctx.guild.id)

            if server_id not in self.data:
                self.data[server_id] = {}

            data_file = self.data_file

            with open(data_file, 'r') as file:
                data = json.load(file)
                balance = data.get(server_id, {}).get(user_id, 0)
            
            embed = disnake.Embed(
                title="💰 Balance 💰",
                description=f"Your balance: ``{balance}`` coins 🪙",
                color=disnake.Color.blue()
            )
            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="baltop", description="Top 10 richest users")
    async def baltop(self, ctx):
        try:
            server_id = str(ctx.guild.id)

            if server_id not in self.data:
                self.data[server_id] = {}

            data_file = self.data_file

            with open(data_file, 'r') as file:
                data = json.load(file)

            server_data = data.get(server_id, {})
            sorted_data = sorted(server_data.items(), key=lambda item: item[1], reverse=True)
            top_users = sorted_data[:10]

            embed = disnake.Embed(title="💰 Top 10 Richest Users 💰", color=disnake.Color.blurple())
            for idx, (user_id, balance) in enumerate(top_users, start=1):
                user = self.bot.get_user(int(user_id))
                if user:
                    embed.add_field(name=f"{idx}. {user.display_name}", value=f"Balance: `{balance}` coins", inline=False)
                else:
                    embed.add_field(name=f"{idx}. User Not Found", value=f"Balance: `{balance}` coins", inline=False)

            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="pay", description="Give coins to another user")
    async def pay(self, ctx, amount: int, user: disnake.Member):
        try:
            if amount <= 0:
                embed = disnake.Embed(
                    title="Invalid Amount",
                    description="The amount must be greater than zero.",
                    color=disnake.Color.red()
                )
                await ctx.response.defer()
                await ctx.send(embed=embed)
                return

            if user.bot:
                embed = disnake.Embed(
                    title="Invalid User",
                    description="You cannot give coins to a bot.",
                    color=disnake.Color.red()
                )
                await ctx.response.defer()
                await ctx.send(embed=embed)
                return

            sender_id = str(ctx.author.id)
            recipient_id = str(user.id)
            server_id = str(ctx.guild.id)

            if server_id not in self.data:
                self.data[server_id] = {}

            data_file = self.data_filea

            with open(data_file, 'r') as file:
                data = json.load(file)

            server_data = data.get(server_id, {})
            sender_balance = server_data.get(sender_id, 0)

            if sender_balance < amount:
                embed = disnake.Embed(
                    title="Insufficient Balance",
                    description="You do not have enough coins to make this transaction.",
                    color=disnake.Color.red()
                )
                await ctx.response.defer()
                await ctx.send(embed=embed)
                return

            with open(data_file, 'r+') as file:
                data = json.load(file)
                server_data = data.get(server_id, {})
                sender_balance = server_data.get(sender_id, 0)
                sender_balance -= amount
                recipient_balance = server_data.get(recipient_id, 0)
                recipient_balance += amount

                server_data[sender_id] = sender_balance
                server_data[recipient_id] = recipient_balance
                data[server_id] = server_data

                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()

            embed = disnake.Embed(
                title="💸 Coins Transferred 💸",
                description=f"You have successfully transferred `{amount}` coins to {user.mention}.",
                color=disnake.Color.green()
            )
            await ctx.response.defer()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(EconomyCommands(bot))
