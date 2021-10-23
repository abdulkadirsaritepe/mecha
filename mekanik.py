# Import necessary libraries
import discord, os, time, json, asyncio, sys
from discord.ext.commands import Bot, HelpCommand, bot, command
from discord.ext import commands
from discord import Embed

# Import mekanik's function files
from cogs.pin import Pin
from cogs.group import Group
from cogs.commands import Commands
from cogs.respond import Respond
from cogs.socialmedia import Youtube, Instagram
from cogs.reaction_check import ReactionCheck
from cogs.reactionapps import ReactionApplications
from cogs.requests import Rates2, Covid2
from cogs.rates import Rates
from cogs.covid import Covid
from cogs.console import Console
from cogs.game import StonePaperScissor, FlipCoin
#from cogs.test import Tests

if sys.platform == "linux":
	rpi_os = True
	import RPi.GPIO as GPIO
	mainDir = "/home/pi/asbot/mekanik" #! 
	logDir = "/home/pi/asbot/Logs" #! 
	adminLogDir = f'{logDir}/admin.json'
else:
	GPIO = None
	rpi_os = False
	mainDir = "C:\Dev\Github\src\mekanik"
	logDir = "C:\Dev\Github\src\mekanik\cogs\Logs"
	adminLogDir = f'{logDir}\\admin.json'

name = "mekanik"
with open(adminLogDir) as adminLogFile:
	data = json.load(adminLogFile)
bot_name = (data[name])["name"]
bot_prefix = (data[name])["prefix"]
bot_token = (data[name])["token"]

# For using some discord features, enable some properties
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True

# Define bot, and give its prefix and intents
client = Bot(command_prefix=bot_prefix, intents=intents)

# Remove help command
client.remove_command('help')

# Start console class
console = Console(client, bot_name)

# Runs when bot has connected
@client.event
async def on_connect():
	print('waiting...')
	# waiting until the bot is ready.
	await client.wait_until_ready()
	# getting console webhook
	await console.get_channel()
	# after bot is ready, the function finishes.
	print(f'{bot_name} is ready.')
	await console.print_console(level=1, number='9990', logText=f'{bot_name} has been started.')

# when the bot is ready, it changes its activity string.
@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(name="with 🛠"))

# Add imported functions
client.add_cog(Commands(client, bot_name, console))
client.add_cog(Youtube(client, console))
client.add_cog(Instagram(client, console))
client.add_cog(ReactionApplications(client, console))
client.add_cog(Pin(client))
client.add_cog(Respond(client))
client.add_cog(ReactionCheck(client))
client.add_cog(Rates(client))
client.add_cog(Rates2(client))
client.add_cog(Covid(client))
client.add_cog(Covid2(client))
client.add_cog(StonePaperScissor(client))

@client.command()
async def close(ctx):
	author = int(ctx.author.id)
	with open(adminLogDir) as adminLogFile:
		data = json.load(adminLogFile)
	if author == int(data["superadmin_id"]):
		await console.print_console(level=1, logText=f'Trying to close {bot_name}...')
		await ctx.message.delete()
		if GPIO != None:
			GPIO.cleanup()
		await client.close()

# Start the bot
client.run(bot_token)

#BOT_SECRET
