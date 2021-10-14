# printing important notes to given discord channel
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
            self.logDir = "/home/pi/asbot/mecha/cogs/Logs" #! 
            self.adminLogDir = f'{self.logDir}/admin.json'
        else:
            rpi_os = False
            self.logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
            self.adminLogDir = f'{self.logDir}\\admin.json'
        self.bot_name = bot_name
        self.console_info = {} # * {"guild":----, "channel":----, "webhook":----}
        self.levels = {0:'```\n[PRINT]', 1:'```re\n[STATE]', 2:'```ini\n[INFO]', 3:'```fix\n[WARN]', 4:'```css\n[ERROR]', 5:'```\n[INPUT]', 6:'```\n[OUTPUT]'}
    
    async def get_console_info(self):
        with open(self.adminLogDir) as adminLogFile:
            data = json.load(adminLogFile)
        try:
            console_guild = self.bot.get_guild(id=int(data["admin_guild"]))
            console_channel = None
            while console_channel == None:
                console_channel = discord.utils.get(console_guild.text_channels, id=int(data["console_channel"]))
            console_webhook = await self.get_webhook((data[str(self.bot_name).lower()])["console_webhook"], console_channel)
            self.console_info = {"guild":console_guild, "channel":console_channel, "webhook":console_webhook}
            await self.print_console(level=2, number='0000', logText=f'Console Webhook has been started! - {str(console_webhook.url)}')
        except Exception as Err:
            print(f'Errorx0000: {Err}')

    async def get_webhook(self, webhook_info, console_channel):
        if webhook_info == None:
            console_webhook = await console_channel.create_webhook(name=f"{self.bot_name} Console")
            with open(self.adminLogDir) as adminLogFile:
                data = json.load(adminLogFile)
            (data[str(self.bot_name).lower()]).update({"console_webhook":int(console_webhook.id)})
            with open(self.adminLogDir, "w") as adminLogFile:
                json.dump(data, adminLogFile)
            print(f'Console Webhook has been created! - {str(console_webhook.url)}')
            return console_webhook
        else:
            try:
                console_webhook = await self.bot.fetch_webhook(webhook_id=int(webhook_info))
                print(f'Console Webhook information has been taken! - {str(console_webhook.url)}')
                return console_webhook
            except:
                try:
                    console_webhook = await console_channel.create_webhook(name=f"{self.bot_name} Console")
                    with open(self.adminLogDir) as adminLogFile:
                        data = json.load(adminLogFile)
                    (data[str(self.bot_name).lower()]).update({"console_webhook":int(console_webhook.id)})
                    with open(self.adminLogDir, "w") as adminLogFile:
                        json.dump(data, adminLogFile)
                    print(f'Console Webhook has been created! - {str(console_webhook.url)}')
                    
                    return console_webhook
                except Exception as Err:
                    print(f'Errorx0001: {Err}')

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
    
        async with aiohttp.ClientSession() as session:
            webhook = None
            while webhook == None:
                try:
                    webhook = Webhook.from_url((self.console_info["webhook"]).url, adapter=AsyncWebhookAdapter(session))
                except:
                    await self.get_console_info()
            avatar_url = 'https://cdn.discordapp.com/attachments/850109861740019722/850110473567469638/pngwing.com_1.png'
            for m in msgs:
                await webhook.send(content=m, username=f'{self.bot_name} Console Log', avatar_url=avatar_url)
