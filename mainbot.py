# Import necessary libraries
import discord, os, json
from discord.ext.commands import Bot, Cog, HelpCommand, bot, command
import sys, os

bot_tag = "main_bot"

def rpi_start(start_type):
	repo_name = "mecha" # TODO
	github_token = "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"
	username = "abdulkadirsaritepe"
	main_dir = "/home/pi/asbot"
	bot_dir = f'{main_dir}/{repo_name}'
	repo = f"https://{github_token}@github.com/{username}/{repo_name}.git"

	commands_dict = {
		"full_start": ["sudo apt-get update", "sudo apt full-upgrade", f"rm -rf {bot_dir}", f"git clone {repo} {bot_dir}", f"pip3 install -U -r {bot_dir}/requirements.txt"], # , f"lxterminal --command='python3 {bot_dir}/mainbot.py'"
		"start": ["sudo apt-get update", "sudo apt-get upgrade", f"rm -rf {bot_dir}", f"git clone {repo} {bot_dir}", f"pip3 install -U -r {bot_dir}/requirements.txt"],
		"quick_start": [f"rm -rf {bot_dir}", f"git clone {repo} {bot_dir}", f"pip3 install -U -r {bot_dir}/requirements.txt"],
		"full_restart": ["sudo reboot"],
		"restart": [f"pip3 install -U -r {bot_dir}/requirements.txt"]
	}

	if not start_type in commands_dict.keys():
		start_type = "start"

	rpiCommands = commands_dict[start_type]

	for cmdText in rpiCommands:
		os.system(cmdText)

if sys.platform == "linux":
	rpi_os = True
	mainDir = "/home/pi/asbot/mecha" #!
	logDir = "/home/pi/asbot/Logs" #!
	adminLogDir = f'{logDir}/admin.json'
	requirementsDir = f'{mainDir}/requirements.txt'
	rpi_start(start_type="start") # TODO
else:
	rpi_os = False
	mainDir = "C:\Dev\Github\src\mecha"
	logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
	adminLogDir = f'{logDir}\\admin.json'

# Import function files
from cogs.console import Console # TODO
		
# Take admin data
with open(adminLogDir) as adminLogFile:
	data = json.load(adminLogFile)
sudo_password = data["sudo_password"]
sudo_password_rpi = data["sudo_password_rpi"]
bot_name = (data[bot_tag])["name"]
bot_prefix = (data[bot_tag])["prefix"]
bot_token = (data[bot_tag])["token"]

# For using some discord features, enable some properties
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True

# Define bot, and give its prefix and intents
client = Bot(command_prefix=bot_prefix, intents=intents)

client.remove_command('help')
# Start console class
console = Console(client, bot_tag)
	
# Runs when bot has connected
@client.event
async def on_connect():
	print('waiting...')
	# getting console webhook
	await console.get_console_info()
	# waiting until the bot is ready.
	await client.wait_until_ready()
	# after bot is ready, the function finishes.
	print(f'{bot_name} is ready.')
	
# when the bot is ready, it changes its activity string.
@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(name="with 🛠"))
	await console.print_console(level=1, number='9990', logText=f'{bot_name} has been started.')

class DiscordBot(Cog):
	def __init__(self, bot, console):
		self.bot = bot
		self.console = console

	@Cog.listener()
	async def on_ready(self):
		await self.system_info()

	async def run_bot(self, discordBotName):
		try:
			await self.console.print_console(level=1, logText=f'Trying to run {discordBotName}...')
			with open(adminLogDir) as adminLogFile:
				data = json.load(adminLogFile)
			if not discordBotName in data.keys():
				await self.console.print_console(level=3, number="9930", logText=f'{discordBotName} has been tried to run, but could not found.')
				return
			if rpi_os == False:
				os.system(f'start cmd /c python {mainDir}\\{discordBotName}.py')
			else:
				os.system(f"lxterminal --command='python3 {mainDir}/{discordBotName}.py'")
			try:
				await self.console.print_console(level=1, number="9900", logText=f'{discordBotName} has been tried to run.')
			except Exception as Err:
				print(f'Errorx9900: {Err}')
		except Exception as Err:
			print(f'Errorx9990: {Err}')
			await self.console.print_console(level=4, number="9990", logText=f'{Err} occured while starting a slave bot.')

	async def system_info(self):
		if rpi_os:
			rpi_ip = os.popen("hostname -I").read() # * 192.168.1.---
			rpi_sys_info = os.popen("cat /proc/version").read() # * Linux version ...
			rpi_temp = os.popen("vcgencmd measure_temp").read() # * temp=40.0'C
			rpi_wlan = os.popen("iwconfig").read() # * wlan0 ...
			await console.print_console(level=1, number='9901', logText=f'Operating System is {sys.platform}.')
			await console.print_console(level=1, number='9902', logText=f'RPi IP adress: {rpi_ip}')
			await console.print_console(level=1, number='9903', logText=f'RPi System Information: {rpi_sys_info}')
			await console.print_console(level=1, number='9904', logText=f'RPi Temperature: {rpi_temp}')
			await console.print_console(level=1, number='9905', logText=f'RPi Wireless: {rpi_wlan}')
		else:
			os_ip = os.popen("ipconfig").read() # * IP Configuration ... 
			#os_sys_info = os.popen("systeminfo").read() # * 
			await console.print_console(level=1, number='9901', logText=f'Operating System is {sys.platform}.')
			await console.print_console(level=1, number='9902', logText=f'OS IP adress: {os_ip}')
			#await console.print_console(level=1, number='9903', logText=f'OS System Information: {os_sys_info}')

	@command()
	async def rpi(self, ctx, info=None):
		await ctx.message.delete()
		if info == None:
			await self.system_info()
		elif str(info).lower() == "ip":
			rpi_ip = os.popen("hostname -I").read() # * 192.168.1.---
			await console.print_console(level=1, number='9902', logText=f'RPi IP adress: {rpi_ip}')
		elif str(info).lower() == "sys":
			rpi_sys_info = os.popen("cat /proc/version").read() # * Linux version ...
			await console.print_console(level=1, number='9903', logText=f'RPi System Information: {rpi_sys_info}')
		elif str(info).lower() == "temp":
			rpi_temp = os.popen("vcgencmd measure_temp").read() # * temp=40.0'C
			await console.print_console(level=1, number='9904', logText=f'RPi Temperature: {rpi_temp}')
		elif str(info).lower() == "ip":
			rpi_wlan = os.popen("iwconfig").read() # * wlan0 ...
			await console.print_console(level=1, number='9905', logText=f'RPi Wireless: {rpi_wlan}')
		
	@command()
	async def run(self, ctx, name=None):
		author = int(ctx.author.id)
		with open(adminLogDir) as adminLogFile:
			data = json.load(adminLogFile)
		if author == int(data["superadmin_id"]) and name != None:
			await console.print_console(level=5, number='9981', logText=f'cmd ~/ run {name}')
			await self.run_bot(name)
			await ctx.message.delete()

	@command()
	async def cmd(self, ctx, *, commandStr):
		await ctx.message.delete()
		author = int(ctx.author.id)
		with open(adminLogDir) as adminLogFile:
			data = json.load(adminLogFile)
		if author == int(data["superadmin_id"]):
			await console.print_console(level=5, number='9900', logText=f'cmd ~/ {commandStr}')
			cmdOutput = os.popen(str(commandStr)).read()
			await console.print_console(level=6, number='9900', logText=f'~/ {cmdOutput}')

	@command()
	async def restart(self, ctx, start_type=None):
		author = int(ctx.author.id)
		with open(adminLogDir) as adminLogFile:
			data = json.load(adminLogFile)
		if author == int(data["superadmin_id"]):
			await console.print_console(level=5, number='9997', logText='cmd ~/ restart')
			await self.console.print_console(level=1, logText=f'Trying to close {bot_name}...')
			await ctx.message.delete()
			await self.bot.close()
			if rpi_os:
				if start_type == "full":
					rpi_start("full_restart")
				elif start_type == "quick":
					rpi_start("quick_start")
				elif start_type == "start":
					rpi_start("start")
				elif start_type == "fullstart":
					rpi_start("full_start")
				else:
					rpi_start("restart")

	@command()
	async def close(self, ctx, start_type=None):
		author = int(ctx.author.id)
		with open(adminLogDir) as adminLogFile:
			data = json.load(adminLogFile)
		if author == int(data["superadmin_id"]):
			await console.print_console(level=5, number='9998', logText='cmd ~/ close')
			await self.console.print_console(level=1, logText=f'Trying to close {bot_name}...')
			await ctx.message.delete()
			await self.bot.close()
			if rpi_os and start_type == "full":
				os.system('poweroff')

# Add functions
client.add_cog(DiscordBot(client, console))

# Start the bot
client.run(bot_token)
