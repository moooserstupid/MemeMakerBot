"""The MemeMakerBot main module file.

Contains code for setting up a logging function, bot intents and the
command that activates the bot (!meme). Also sets up a config file and
config parser that can be used to configure bot prefixes and commands.
"""

__version__ = '1.0'
__author__ = 'Ali Asghar'

# Standard library imports
import os
import logging
from configparser import ConfigParser
from dotenv import load_dotenv
# Discord and discord extensions library imports
import discord
from discord.ext import commands

# Setup of a logging system. The logger contained in Discord.py is used
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setting up bot intents
intents  = discord.Intents.default()
intents.typing = False
intents.presences = False

#Settign up a config file and a config parser. Used to read bot prefixes
config = ConfigParser()
config.read('config.ini')
prefix = config['Bot Prefixes']['prefix']
altprefix = config['Bot Prefixes']['altprefix']
bot = commands.Bot(command_prefix=[prefix, altprefix], intents = intents)


@bot.event
async def on_ready():
    """Function called as soon as the bot connects to discord."""
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='meme', help='Command used to activate the bot.')
async def meme(ctx):
    """Bot activation command

    Creates a dm channel (if not already created) with the user that
    used the command.
    """
    dm_channel = await ctx.author.create_dm()
    try:
        bot.load_extension(f'cogs.query')
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(
                    "Bot activated! You can now use the !find"
                    "command to search for the background image"
                    "or use !upload to upload your own.")
            return
        await dm_channel.send(
                    "Bot activated! You can now use the !find"
                    "command to search for the background image"
                    "or use !upload to upload your own.")
    except commands.ExtensionAlreadyLoaded:
        await dm_channel.send("The bot is already active.")


@bot.command()
async def refresh(ctx):
    """Debugging command for refreshing the editor cog.

    Reloads the editor cog. Will be removed in final version.
    """
    bot.unload_extension(f'cogs.editor')
    bot.load_extension(f'cogs.editor')
    await ctx.send("refreshed.")

# Loading Bot Discord Token from the .env file.
load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)