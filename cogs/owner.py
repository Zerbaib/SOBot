import json
import subprocess
import sys

import disnake
import requests
from disnake.ext import commands

from utils import error, var


class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.online_version_url = var.online_version
        self.local_version = var.local_version

    @commands.Cog.listener()
    async def on_ready(self):
        print('========== ⚙️ Owner ⚙️ ==========')
        print('🔩 /check has been loaded')
        print('🔩 /update has been loaded')
        print('🔩 /restart has been loaded')
        print('🔩 /stop has been loaded')
        print()

    def get_local_version(self):
        with open(self.local_version, "r") as version_file:
            local_version = version_file.read().strip()
        return local_version


    @commands.slash_command(name="check", description="Check if the bot is up to date")
    @commands.is_owner()
    async def check(self, ctx):
        try:
            
            response = requests.get(self.online_version_url)
            if response.status_code == 200:
                online_version = response.text.strip()
                local_version = self.get_local_version()

                embed = disnake.Embed(
                    title=f"🔎 Check of {self.bot.user.name}",
                )
                if online_version == local_version:
                    embed.description = "The bot is up to date. 👍"
                    embed.colour = disnake.Color.brand_green()
                else:
                    embed.description = "An update is available. 👎"
                    embed.colour = disnake.Color.brand_red()

                embed.add_field(name="Local Version", value=f"```{local_version}```", inline=True)
                embed.add_field(name="Online Version", value=f"```{online_version}```", inline=True)
                await ctx.response.defer()
                await ctx.send(embed=embed)

        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="update", description="Get the latest update of the bot")
    @commands.is_owner()
    async def update(self, ctx):
        try:
            with open("config.json", 'r') as config_file:
                config = json.load(config_file)
            
            embed = disnake.Embed(
                title=f"⤴️ Update of ``{self.bot.user.name}``",
                description=f"Please wait...",
                color=disnake.Color.old_blurple()
            )
            await ctx.send(embed=embed)

            update_process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = update_process.communicate()

            if update_process.returncode == 0:
                success_embed = disnake.Embed(
                    title=f"⤴️ Update of ``{self.bot.user.name}``",
                    description="✅ Update successful!\nYou just need a restart to apply the update.",
                    color=disnake.Color.brand_green()
                )
                await ctx.send(embed=success_embed)
            else:
                error_message = stderr.decode("utf-8")
                error_embed = disnake.Embed(
                    title=f"↩️ Error during the ``/update``",
                    description=f"```{error_message}```",
                    color=disnake.Color.brand_red()
                )
                await ctx.send(embed=error_embed)

        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)


    @commands.slash_command(name="restart", description="Restart the bot")
    @commands.is_owner()
    async def restart(self, ctx):
        try:
            embed = disnake.Embed(
                title="🔄 Restarting... 🔄",
                description="The bot is restarting. Please wait...",
                color=disnake.Color.old_blurple()
            )
            await ctx.response.defer()
            await ctx.send(embed=embed)
            python = sys.executable
            subprocess.Popen([python, "main.py"])
            sys.exit()

        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

    @commands.slash_command(name="stop", description="Stop the bot")
    @commands.is_owner()
    async def stop(self, ctx):
        try:
            await ctx.send("🛑 Stopping the bot... 🛑", ephemeral=True)
            await self.bot.close()
        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))