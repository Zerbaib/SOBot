import json
import os
import platform
import aiohttp
import disnake
from disnake.ext import commands
from utils import var

if not os.path.exists(var.data_folder):
    os.makedirs(var.data_folder)
for file in var.data_file:
    if not os.path.exists(file):
        with open(file, 'w') as data_file:
            json.dump({}, data_file)
for filename in os.listdir(var.data_folder):
    if filename not in var.data_file:
        file_path = os.path.join(var.data_folder, filename)
        os.remove(file_path)

#if not os.path.exists(badWord_file_path):
#    badword_data = {
#        "bad_words": [
#            "badword1",
#            "badword2",
#            "badword3"
#        ]
#    }
#    with open(badWord_file_path, 'w') as badword_file:
#        json.dump(badword_data, badword_file, indent=4)

if not os.path.exists(var.config_file_path):
    with open(var.config_file_path, 'w') as config_file:
        token = input("Enter the bot's token:\n")
        prefix = input("Enter the bot's prefix:\n")
        config_data = {
            "TOKEN": token,
            "PREFIX": prefix
        }
        json.dump(config_data, config_file, indent=4)
    with open(var.config_file_path, 'r') as config_file:
        config = json.load(config_file)
else:
    with open(var.config_file_path, 'r') as config_file:
        config = json.load(config_file)

token = config["TOKEN"]
prefix = config["PREFIX"]

bot = commands.Bot(
    command_prefix=prefix,
    intents=disnake.Intents.all(),
    case_insensitive=True
)
bot.remove_command('help')

@bot.event
async def on_ready():
    if bot.user.discriminator == 0:
        nbot = bot.user.name
    else:
        nbot = bot.user.name + "#" + bot.user.discriminator

    async with aiohttp.ClientSession() as session:
        async with session.get(var.online_version) as response:
            if response.status == 200:
                bot_repo_version = await response.text()
            else:
                bot_repo_version = "Unknown"

    with open(var.local_version, 'r') as version_file:
        bot_version = version_file.read().strip()

    if bot_version != bot_repo_version:
        print()
        print('===============================================')
        print('🛑 You are not using the latest version!')
        print('🛑 Please update the bot.')
        print('🛑 Use "git fetch && git pull" to update your bot.')
    print('===============================================')
    print(f"🔱 The bot is ready!")
    print(f'🔱 Logged in as {nbot} | {bot.user.id}')
    print(f'🔱 Bot local version: {bot_version}')
    print(f'🔱 Bot online version: {bot_repo_version}')
    print(f"🔱 Disnake version: {disnake.__version__}")
    print(f"🔱 Running on {platform.system()} {platform.release()} {os.name}")
    print(f"🔱 Python version: {platform.python_version()}")
    print('===============================================')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        cog_name = filename[:-3]
        try:
            bot.load_extension(f'cogs.{cog_name}')
        except Exception as e:
            print(f"🌪️  Error during '{cog_name}' loading:\n\n{e}")

bot.run(token)