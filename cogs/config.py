import json
import os

import disnake
from disnake.ext import commands

from utils import error, var


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_folder = var.config_folder
        self.default_config = var.default_config
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            config_path = f"{self.config_folder}{guild.id}.json"
            if not os.path.exists(config_path):
                with open(config_path, "w") as config_file:
                    json.dump(self.default_config, config_file, indent=4)
        print('========== ⚙️ Config ⚙️ ==========')
        print('🧰 config has been loaded')
        print()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        default_config = self.default_config
        with open(f"{self.config_folder}{guild.id}.json", "w") as config_file:
            json.dump(default_config, config_file, indent=4)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        os.remove(f"{self.config_folder}{guild.id}.json")

def setup(bot):
    bot.add_cog(ConfigCog(bot))