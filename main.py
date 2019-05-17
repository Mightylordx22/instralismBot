import asyncio
import discord
import sqlite3 as sql
from updateData import update
import json
import urllib.request
import requests
from steam import SteamID
from discord import Member
from discord.ext import commands
from discord.ext.commands import CommandNotFound

botCommands = ["rank", "help", "updatedata","addbot","shutdown","steam","top10","myrank"]
bot = commands.Bot(command_prefix="!")
with open("botToken.txt") as file:
    botToken = file.read().split(":")[1]
with open("steamWebAPI.txt") as file:
    steamWebAPI = file.read().split(":")[1]

def chooseColour(place):
    colour = 0x494a4c
    if place > 0 and place < 11:
        colour = 0xe0cd1f
    elif place > 10 and place < 26:
        colour = 0xe718f2
    elif place > 25 and place < 101:
        colour = 0xf22b2b
    elif place > 100 and place < 501:
        colour = 0x44a7e5
    else:
        colour = 0x494747
    return colour

@bot.event
async def on_ready():
    print("bot online")

@bot.command()
async def rank(ctx, *args):
    """Shows all !rank commands
    !rank < @mention >
    !rank < steam profile link >
    !rank < number >
    !rank < steam 64 id >"""
    conn = sql.connect("data.db")
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM data").fetchall()
    author = ctx.author.mention
    gotID = False
    steamID = ""
    if len(args) == 0:
        await ctx.send(f"{author}, that is not valid type !help rank")
    elif len(args) > 1:
        await ctx.send(f"{author}, you can only have 1 argument")
    else:
        queried = args[0]
        if queried.isdigit() is True:
            if queried[0:6] == "765611":
                steamID = queried
                gotID = True
            else:
                for i in data:
                    if i[1] == int(queried):
                        steamID = i[0]
                        gotID = True
        else:
            if queried[:30] == "https://steamcommunity.com/id/":
                steamID = str(SteamID.from_url(queried, http_timeout=10))
                gotID = True
            elif queried[:36] == "https://steamcommunity.com/profiles/":
                steamID = str(SteamID.from_url(queried, http_timeout=10))
                gotID = True
            elif queried[0] == '<' and queried[-1:] == '>':
                user = await commands.MemberConverter().convert(ctx, args[0])
                try:
                    steamID = cursor.execute(f"SELECT steamID FROM users WHERE nickname = '{user}'").fetchone()[0]
                    if steamID is not None:
                        gotID = True
                except:
                    await ctx.send("That person hasn't linked their steam")
            else:
                await ctx.send("Sorry that is not valid see !help ranks")
        if gotID is True:
            for i in data:
                if i[0] == steamID:
                    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steamWebAPI}&format=json&steamids={steamID}"
                    data = json.loads(urllib.request.urlopen(url).read().decode("UTF-8"))
                    picture = data["response"]["players"][0]["avatarfull"]
                    embed = discord.Embed(color=chooseColour(i[1]))
                    embed.set_author(name=f'{data["response"]["players"][0]["personaname"]}\'s Stats',
                                     icon_url=data["response"]["players"][0]["avatar"])
                    embed.add_field(name="Name",
                                    value=f"[{data['response']['players'][0]['personaname']}]({data['response']['players'][0]['profileurl']})",
                                    inline=True)
                    embed.add_field(name="Place", value=i[1], inline=True)
                    embed.add_field(name="Total Score", value=i[2], inline=True)
                    embed.add_field(name="Average Accuracy", value=i[3], inline=True)
                    embed.add_field(name="Average Misses", value=i[4], inline=True)
                    embed.add_field(name="Last Updated", value=i[5], inline=True)
                    embed.set_thumbnail(url=picture)
                    embed.set_footer(text="Made By MighTy")
            await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def myrank(ctx, *args):
    """Shows the position of a the user who typed the command
    !myrank"""
    author = ctx.author.mention
    if len(args) != 0:
        await ctx.send(f"{author},You don't need any arguments for this command")
    else:
        conn = sql.connect("data.db")
        cursor = conn.cursor()
        if cursor.execute(f"""SELECT * FROM data WHERE steamID = '{cursor.execute(f"SELECT steamID FROM users WHERE nickname = '{ctx.author}'").fetchone()[0]}'""").fetchone() != None:
            steamID = cursor.execute(f"SELECT steamID FROM users WHERE nickname = '{ctx.author}'").fetchone()[0]
            data = json.loads(requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
                                params={"key": steamWebAPI, "format": "json", "steamids": steamID}).text)
            i = cursor.execute(f"SELECT * FROM data WHERE steamID = '{steamID}'").fetchone()
            picture = data["response"]["players"][0]["avatarfull"]
            embed = discord.Embed(color=chooseColour(i[1]))
            embed.set_author(name=f'{data["response"]["players"][0]["personaname"]}\'s Stats',
                             icon_url=data["response"]["players"][0]["avatar"])
            embed.add_field(name="Name",
                            value=f"[{data['response']['players'][0]['personaname']}]({data['response']['players'][0]['profileurl']})",
                            inline=True)
            embed.add_field(name="Place", value=i[1], inline=True)
            embed.add_field(name="Total Score", value=i[2], inline=True)
            embed.add_field(name="Average Accuracy", value=i[3], inline=True)
            embed.add_field(name="Average Misses", value=i[4], inline=True)
            embed.add_field(name="Last Updated", value=i[5], inline=True)
            embed.set_thumbnail(url=picture)
            embed.set_footer(text="Made By MighTy")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{author}, Sorry couldn't find any information")

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_role("Admin")
async def shutdown(ctx):
    await ctx.send("The bot is now shutting down, goodbye:wave:")
    await bot.logout()

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_role("Admin")
async def updatedata(ctx):
    """Updates Player Data"""
    update()
    await ctx.send(f"{ctx.author.mention}, Updated Data!")

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def top10(ctx, *args):
    """Shows the top 10 ranked players
    !top 10 Shows the top 10 players"""
    conn = sql.connect("data.db")
    cursor = conn.cursor()
    sqlData = cursor.execute("SELECT * FROM data").fetchall()
    finalString = ""
    if len(args) != 0:
        await ctx.send(f"{ctx.author.mention}, See !help top10.")
    else:
        for i in range(0, 10):
            url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steamWebAPI}&format=json&steamids={sqlData[i][0]}"
            data = json.loads(urllib.request.urlopen(url).read().decode("UTF-8"))
            finalString += f"[ {i+1} ]  :   ['{data['response']['players'][0]['personaname']}']({data['response']['players'][0]['profileurl']})\n"
        embed = discord.Embed(title="**Top 10 Ranked Players**", color=0xe0cd1f, description=finalString)
        embed.set_thumbnail(url="https://intralism.khb-soft.ru/images/logo.png")
        embed.set_footer(text="Made by MighTy")
        await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def addbot(ctx):
    """Provides an embed so you can add the bot to your own server"""
    embed = discord.Embed(color=0xdbf330)
    embed.set_author(name="Invite me to your server!", icon_url='https://intralism.khb-soft.ru/images/logo.png')
    embed.add_field(name="**Here is my invite link**",
                    value="**https://discordapp.com/oauth2/authorize?client_id=467763787097833492&scope=bot&permissions=305187840**",
                    inline=False)
    embed.add_field(name="**Have more fun here**",
                    value="**[Offical Intralism Discord](https://discord.gg/intralism)**", inline=False)
    embed.set_footer(text="Made by MighTy")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(f"{ctx.author.mention}, that's not a command. See !help for more")
    raise error

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention}, please wait {int(error.retry_after)} seconds before using that command.")
    raise error

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"{ctx.author.mention}, you don't have enough permission for this command.")
    raise error

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def steam(ctx, *args):
    """Link your steam account to your profile
    !steam < steam link >"""
    author = ctx.author.mention
    if len(args) == 0:
        await ctx.send(f"{author}, incorrect format please see !help steam")
    elif len(args) > 1:
        await ctx.send(f"{author}, inccorect format please see !help steam")
    else:
        steamID = str(SteamID.from_url(f"{args[0]}", http_timeout=10))
        if steamID == "None":
            await ctx.send(f"{author}, sorry that is not a valid link.")
        else:
            conn = sql.connect("data.db")
            cursor = conn.cursor()
            if cursor.execute(f"SELECT * FROM users WHERE nickname = '{ctx.author}';").fetchone() == None:
                cursor.execute(f"""INSERT INTO users(steamID, nickname) VALUES ('{steamID}','{ctx.author}')""")
            else:
                cursor.execute(f"UPDATE users SET steamID = '{steamID}' WHERE nickname = '{ctx.author}'")
            conn.commit()
            await ctx.send(f"{author}, success you're accounts are now linked.")

if __name__ == "__main__":
    conn = sql.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
	userID INTEGER PRIMARY KEY autoincrement,
    steamID CHAR(17) ,
    nickname VARCHAR(32)
    );""")
    conn.commit()
    conn.close()
    bot.run(botToken)