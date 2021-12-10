import json
from logging import exception
import os
import platform
import random
import sys
import time
import sqlite3
import random

import mysql.connector
import aiohttp
import discord
import datetime
from discord.ext import commands
from discord.ext.commands.core import Command, command
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from helpers import checks

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mydb = sqlite3.connect(r"./main.db")
        self.info = self.mydb.cursor()

    def check_balance(self, user_id):
        self.info.execute(
            "SELECT account_val FROM accounts WHERE user_id = ?", [user_id]
        )
        return self.info.fetchone()

    def check_item(self, item_id):
        self.info.execute("SELECT * FROM items WHERE item_id = ?", [item_id])
        return self.info.fetchall()

    @commands.command()
    async def create(self, ctx):
        await ctx.message.delete()
        self.info.execute(
            f"SELECT user_id FROM accounts where user_id = {ctx.author.id}"
        )
        if self.info.fetchone() == None:
            self.info.execute(
                f"INSERT INTO accounts VALUES ({ctx.author.id}, 0, '{ctx.author.name}', 500, 0, 0)"
            )

            embed = discord.Embed(color=0x7604B4)
            embed.add_field(
                name=f"Created an account for {ctx.author.name}",
                value="Access it using !account",
                inline=False,
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0x7604B4)
            embed.add_field(
                name=f"{ctx.author.name}, it looks like you already have an account.",
                value="Access it using **!account**",
                inline=False,
            )
            await ctx.send(embed=embed)
        self.mydb.commit()

    @commands.command()
    async def account(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if not member:
            member = ctx.author

        self.info.execute(f"SELECT * FROM accounts where user_id = {ctx.author.id}")
        data = self.info.fetchall()

        for entry in data:
            user_name = entry[2]
            account_val = entry[3]
            items_pch = entry[4]

        embed = discord.Embed(
            title="Account", description=f"{user_name}'s account:", color=0x7604B4
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(
            name=f"Account: ${account_val}\nItems purchased: {items_pch}\n",
            value="\u200b",
            inline=True,
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="NCL")
        await ctx.send(embed=embed)

    @commands.command()
    async def list(self, ctx, item_desc, item_url, item_price: int):
        await ctx.message.delete()
        lines = (
            open(r"./item_id.txt").read().splitlines()
        )
        item_id = random.choice(lines)
        print(item_id)

        with open(r"./item_id.txt", "r") as f:
            lines2 = f.readlines()

        with open(r"./item_id.txt", "w") as f:
            for line in lines2:
                if line.strip("\n") != item_id:
                    f.write(line)

        self.info.execute(f"SELECT item_id FROM items where item_id = {item_id}")
        if self.info.fetchone() == None:
            self.info.execute(
                f"INSERT INTO items VALUES ({item_id}, {ctx.author.id}, '{item_desc}', {item_price}, '{item_url}')"
            )

            embed = discord.Embed(color=0x7604B4)
            embed.add_field(
                name="Item Listed",
                value=f" Item Description: **{item_desc}**\n Price: **{item_price}**\nID: **{item_id}**\nOwner: **{ctx.author.id}**",
                inline=False,
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0x7604B4)
            embed.add_field(
                name=f"There's already an active listing with this ID.\nPlease contact Support **ASAP**.",
                value="\u200b",
                inline=False,
            )
            await ctx.send(embed=embed)
        self.mydb.commit()

    @commands.command()
    async def buy(self, ctx, item_id):
        await ctx.message.delete()
        self.info.execute(f"SELECT item_id FROM items where item_id = {item_id}")
        if self.info.fetchone() == None:
            await ctx.send('No products found for: {item_id}')

        else:

            author_balance = self.check_balance(ctx.author.id)
            item_info = self.check_item(item_id)
            user_result = self.info.fetchall()

            for ent in item_info:
                item_id = ent[0]
                owner_id = ent[1]
                item_desc = ent[2]
                item_price = ent[3]
                item_url = ent[4]

            if author_balance[0] < item_price:
                embed = discord.Embed(color=0x7604B4)
                embed.add_field(
                    name=f"Not enough money!",
                    value=f"Price: {item_price}",
                    inline=False,
                )
                await ctx.send(embed=embed)

            else:
                self.info.execute(
                    f"SELECT account_val FROM accounts WHERE user_id = {ctx.author.id}"
                )
                data = self.info.fetchall()
                for entry in data:
                    NewMoney = author_balance[0] - item_price
                    sql = f"UPDATE accounts SET account_val = {NewMoney} WHERE user_id = {ctx.author.id}"
                    self.info.execute(sql)
                    self.mydb.commit()

                embed = discord.Embed(color=0x7604B4)
                embed.add_field(
                    name=f"Purchesed- {item_id}",
                    value="Please check your private messages.",
                    inline=False,
                )
                await ctx.send(embed=embed)
                embed = discord.Embed(color=0x7604B4)
                embed.add_field(
                    name=f"Item: {item_desc}",
                    value=f"Remember **not** to share this link with anyone but yourself.\nURL: ||{item_url}||\n\nItem-ID: **{item_id}**",
                    inline=False,
                )
                await ctx.author.send(embed=embed)

    @commands.command()
    async def genlist(self, ctx):
        textfile = open(r"./item_id.txt", "w")
        list = []
        for i in range(9999):
            r = random.randint(1000, 9999)
            if r not in list:
                list.append(r)
            textfile.write(str(i) + "\n")

        textfile.close()
        await ctx.send('Done.')


def setup(bot):
    bot.add_cog(general(bot))
