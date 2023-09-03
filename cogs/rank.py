import json
import os
import random

import disnake
from disnake.ext import commands

from utils import error, var


class RankCommands(commands.Cog):
    def __init__(self, bot, base_level, level_factor):
        self.bot = bot
        self.base_level = base_level
        self.level_factor = level_factor
        self.data_path = var.rank_data_file_path
        self.data = {}
        self.load_data()

    @commands.Cog.listener()
    async def on_ready(self):
        print('========== ⚙️ Rank ⚙️ ==========')
        print('🔩 /rank has been loaded')
        print('🔩 /leaderboard has been loaded')
        print()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        server_id = str(message.guild.id)
        user_id = str(message.author.id)

        if server_id not in self.data:
            self.data[server_id] = {}

        if user_id not in self.data[server_id]:
            self.data[server_id][user_id] = {"xp": 0, "level": 0}

        self.data[server_id][user_id]["xp"] += random.randint(1, 5)
        xp = self.data[server_id][user_id]["xp"]
        lvl = self.data[server_id][user_id]["level"]

        xp_required = 5 * (lvl ** 2) + 10 * lvl + 10

        if xp >= xp_required:
            lvl = lvl + 1
            self.data[server_id][user_id]["level"] = lvl
            xp_required = 5 * (lvl ** 2) + 10 * lvl + 10
            embed = disnake.Embed(
                title=f'👏 Congratulations, {message.author.name}! 👏',
                description=f'**You reached level **```{lvl}```\n*You need ``{xp_required}`` xp for the next level*',
                color=disnake.Color.brand_green()
            )

            msg = await message.channel.send(embed=embed)

        self.save_data()

    @commands.slash_command(name='rank', description='Displays your current rank or the rank of a user')
    async def rank(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        try:
            server_id = str(inter.guild.id)
            user_id = str(inter.author.id)
            user_name = str(inter.author.name)

            if server_id in self.data and user_id in self.data[server_id]:
                xp = self.data[server_id][user_id]["xp"]
                level = self.data[server_id][user_id]["level"]
                xp_required = 5 * (level ** 2) + 10 * level + 10
                user_rank = self.get_user_rank(server_id, user_id)
                embed = disnake.Embed(
                    title=f"🔰 {user_name}'s rank -> #{user_rank} 🔰",
                    description=f'**Level:** ```{level}```\n**XP:** ``{xp}``\n*Need* ``{xp_required}`` *to win one level*',
                    color=disnake.Color.blurple()
                )

                await inter.response.send_message(embed=embed)
            else:
                await inter.response.send_message(f'{user_name} does not have a rank yet.')
        except Exception as e:
            embed = error.error_embed(e)
            await inter.send(embed=embed)

    @commands.slash_command(name='leaderboard', description='Show the top 10 xp leaderboard')
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        try:
            if not self.data:
                await inter.response.send_message("No ranking data available.")
                return

            server_id = str(inter.guild.id)
            if server_id in self.data:
                server_data = self.data[server_id]
                sorted_users = sorted(server_data.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
                embed = disnake.Embed(title="💯 Leaderboard 💯", color=disnake.Color.blurple())
                for i, (user_id, user_data) in enumerate(sorted_users):
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        embed.add_field(name=f"{i+1}. {user.name}", value=f"```Level: {user_data['level']} | XP: {user_data['xp']}```", inline=False)
                    except disnake.NotFound:
                        pass
                    if i == 9:
                        break
                await inter.send(embed=embed)
            else:
                await inter.response.send_message("No ranking data available for this server.")
        except Exception as e:
            embed = error.error_embed(e)
            await inter.send(embed=embed)

    def get_user_rank(self, server_id, user_id):
        if server_id in self.data:
            sorted_ranks = sorted(self.data[server_id].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
            for i, (id, _) in enumerate(sorted_ranks):
                if id == user_id:
                    return i + 1

        return -1

    def save_data(self):
        with open(self.data_path, 'w') as data_file:
            json.dump(self.data, data_file, indent=4)

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as data_file:
                self.data = json.load(data_file)

def setup(bot):
    bot.add_cog(RankCommands(bot, base_level=1, level_factor=0.1))
