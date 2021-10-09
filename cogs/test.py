from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import Embed
import time, discord, aiohttp, json

def updateJsonFile():
    data = {'serverlogs':{}, 'applications':{}}
    data = json.dumps(data, indent=4)
    with open('C:\Dev\github\src\mekanik\cogs\logs.json', 'a') as f:
        f.truncate(0)
        f.write(data)
        print('Updated!')


updateJsonFile()