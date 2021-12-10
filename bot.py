import json
import os
import platform
import random
import sys
import sqlite3
import json

import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext
from tabulate import tabulate
from flask import Flask

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found!")
else:
    with open("config.json") as file:
        config = json.load(file)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "main.db")
mydb = sqlite3.connect(db_path)
info = mydb.cursor()

intents = discord.Intents.default()

bot = Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")

@bot.event
async def on_member_join(member):
    info.execute(f"SELECT user_id FROM users where user_id = {member.id}")
    if info.fetchone() == None:
        info.execute(
            f"INSERT INTO accounts VALUES ({member.author.id}, 0, '{member.author.name}', 500, 0, 0)"
        )
    else:
        pass
    mydb.commit()


bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_slash_command(ctx: SlashContext):
    full_command_name = ctx.name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    print(
        f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})"
    )


if __name__ == "__main__":
    bot.run(config["token"])
