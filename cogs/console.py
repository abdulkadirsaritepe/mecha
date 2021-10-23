# printing important notes to given discord channel
from logging import error
import re
from discord import message, Webhook, AsyncWebhookAdapter, webhook
from discord.embeds import Embed
from discord.ext.commands import Cog, command
from discord.ext import commands
import datetime, discord, aiohttp, json, sys

class Console(Cog):
    def __init__(self, bot, bot_name):
        self.bot = bot
        if sys.platform == "linux":
            rpi_os = True
            self.logDir = "/home/pi/asbot/Logs" #! 
            self.adminLogDir = f'{self.logDir}/admin.json'
        else:
            rpi_os = False
            self.logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
            self.adminLogDir = f'{self.logDir}\\admin.json'
        self.bot_name = bot_name
        self.console_info = {} # * {"guild":----, "channel":----, "webhook":----}
        self.console_channel = None
        self.levels = {0:'```\n[PRINT]', 1:'```re\n[STATE]', 2:'```ini\n[INFO]', 3:'```fix\n[WARN]', 4:'```css\n[ERROR]', 5:'```\n[INPUT]', 6:'```\n[OUTPUT]'}

    async def get_channel(self):
        with open(self.adminLogDir) as adminLogFile:
            data = json.load(adminLogFile)
        try:
            console_guild = None
            while console_guild == None:
                console_guild = self.bot.get_guild(id=int(data["admin_guild"]))
            console_channel = None
            while console_channel == None:
                console_channel = discord.utils.get(console_guild.text_channels, id=int(data["console_channel"]))
            self.console_channel = console_channel
            await self.print_console(level=2, number='0000', logText=f'Console Channel Id has been taken! - {str(console_channel.id)}')
        except Exception as Err:
            print(f'Errorx0000: {Err}')

    async def print_console(self, level=2, number='9999', logText='Empty'):
        logIndicator = self.levels[int(level)]
        msgs = []
        if len(logText) > 1950:
            logTexts = []
            for k in range(0, len(logText), 1950):
                logTexts.append(logText[k:k+1950])
        else:
            logTexts = [logText]
        for m in logTexts:
            msg = f'{str(logIndicator)} [x{str(number)}] - {str(m)}```'
            msgs.append(msg)
        for m in msgs:
            error0020 = True
            while error0020:
                try:
                    await self.console_channel.send(m)
                    error0020 = False
                except:
                    await self.get_channel()
