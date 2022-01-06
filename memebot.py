
# bot.py
import os
from io import BytesIO
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv
from configparser import ConfigParser
from PIL import Image
# import asyncio
from timer import Timer
import aiohttp
import imagesearch
import caption

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents  = discord.Intents.default()
intents.typing = False
intents.presences = False


config = ConfigParser()
config.read('config.ini')

prefix = config['Bot Prefixes']['prefix']
altprefix = config['Bot Prefixes']['altprefix']


load_dotenv()
discordToken = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=[prefix, altprefix], intents = intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='meme', help='Helps you create the perfect meme.')
async def meme(ctx):
    try:
        bot.load_extension(f'cogs.query')
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Bot activated! You can now use the !find command to search for a background image or use !upload to upload your own.")
            return    
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send("Bot activated! You can now use the find command to search for the background image or use !upload to upload your own.")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send("The bot is already active.")
@bot.command()
async def refresh(ctx):
    bot.unload_extension(f'cogs.editor')
    bot.load_extension(f'cogs.editor')
    await ctx.send("refreshed.")

bot.run(discordToken)