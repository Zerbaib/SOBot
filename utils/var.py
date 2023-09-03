# Description: All var of the bot

#badWord_file_path = "bad_words.json"

# Config var
config_file_path = "./config.json"
config_folder = "./config/"
default_config = {}

# Casino var
slot_emoji = ["🍒", "🍊", "🍋", "🍇", "🔔", "💎", "🍀", "🍎"]
cooldown_time = 60 * 60 * 2

# Data
data_folder = "./data/"
user_data_file_path = f"{data_folder}users.json"
economy_data_file_path = f"{data_folder}economy.json"
rank_data_file_path = f"{data_folder}ranks.json"
casino_cooldown_data_file_path = f"{data_folder}cooldown.json"

# Repos Github and version link
online_version = "https://raw.githubusercontent.com/Zerbaib/SOBot/main/version"
issues_link = "https://github.com/Zerbaib/SOBot/issues/new?assignees=Zerbaib&labels=bug"
local_version = "./version"

# List and dict
data_file = [
    user_data_file_path, 
    economy_data_file_path, 
    rank_data_file_path, 
    casino_cooldown_data_file_path
]