import discord, aiohttp, asyncio, json, sys
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command
from discord import Embed, File
from PIL import Image, ImageFont, ImageDraw

# The class checks new covid-19 data, and sends notification to the given channels at the given guilds.
# Also, it sends a message when '&covid' is typed.
class Covid(Cog):
    def __init__(self, bot):
        self.bot = bot
        if sys.platform == "linux":
            rpi_os = True
            self.imagesDir = "/home/pi/asbot/mekanik/cogs/Images" #! 
            self.logDir = "/home/pi/asbot/mekanik/cogs/Logs" #! 
            self.covidLogDir = f'{self.logDir}/updates.json'
        else:
            rpi_os = False
            self.imagesDir = "C:/Dev/Github/src/mekanik/cogs/Images"
            self.logDir = "C:\Dev\Github\src\mekanik\cogs\Logs"
            self.covidLogDir = f'{self.logDir}\\updates.json'
        # Dictionary of guilds and related channels. 
        # Format: guild.id:channel.id
        self.channels = {}
        self.get_covid_channels()
        # The variable stores the date of the last updated data
        self.lastUpdate = 0

    @Cog.listener()
    async def on_ready(self):
        # when the bot is ready, it is started.
        self.covidUpdate.start()

    def get_covid_channels(self):
        with open(self.covidLogDir) as covidLogFile:
            data = json.load(covidLogFile)
        for guildId in data.keys():
            self.channels.update({int(guildId):(data[guildId])["covid_channel"]})

    async def covid19(self):
        covidsite = "https://covid19.saglik.gov.tr/"
        async with aiohttp.ClientSession() as session:
            async with session.get(covidsite) as response:
                req = await response.text()
        info = (req.split("var sondurumjson = ["))[1]
        info = ((str(info)).split("];//]]"))[0]
        info = (info.split("];var haftalikdurumjson = ["))
        daily = eval(info[0])
        weekly = eval(info[1])
        daily.update({"toplam_vefat":weekly["toplam_vefat_sayisi"]})
        daily.update({"toplam_vaka":weekly["toplam_vaka_sayisi"]})
        # * Parameters = tarih, gunluk_test, gunluk_vaka, gunluk_hasta, gunluk_vefat, gunluk_iyilesen, toplam_test, toplam_hasta, toplam_vefat, toplam_iyilesen, toplam_yogun_bakim,
        # * toplam_entube, hastalarda_zaturre_oran, agir_hasta_sayisi, yatak_doluluk_orani, eriskin_yogun_bakim_doluluk_orani, ventilator_doluluk_orani, 
        # * ortalama_filyasyon_suresi, ortalama_temasli_tespit_suresi, filyasyon_orani
        return daily
    
    async def editCovidImage(self, path, info):
        # edit the message image template according to the latest data
        img = Image.open(path)
        font1 = ImageFont.truetype(f'{self.imagesDir}/futura-bold/futura-bold.otf', 200) #!
        font2 = ImageFont.truetype(f'{self.imagesDir}/futura-bold/futura-bold.otf', 120) #!
        image_editable = ImageDraw.Draw(img)
        titles = [["gunluk_test", "gunluk_vaka", "gunluk_hasta", "gunluk_vefat", "gunluk_iyilesen"], ["toplam_test", "toplam_vaka", "toplam_vefat", "agir_hasta_sayisi", "toplam_iyilesen"]]
        x, y = 3100, 1525
        for k in titles:
            for l in k:
                image_editable.text((x, y), info[l], (255, 255, 255), anchor="rt", font=font1)
                y+=540
            x+=3550
            y=1525
        date = info["tarih"]
        image_editable.text((5950, 4300), date, (255, 255, 255), font=font2)
        # save the image to the certain directory
        img.save(f'{self.imagesDir}/covidresult.png') #!

    @command(name='covid')
    async def covid(self, ctx):
        # when a user sends '&covid', try to send the information message
        try:
            await ctx.send(file=File(f'{self.imagesDir}/covidresult.png')) #!
        # if some error occurs, print it.
        except Exception as err:
            print(f'ERROR! Covid- {err}')

    @tasks.loop(seconds=60.0)
    async def covidUpdate(self):
        # loop function for checking covid info
        # path: template image directory
        path = f'{self.imagesDir}/covidtable.png' #!
        # get the latest info
        info = await self.covid19()
        # if lastupdate == 0, just update the lastupdate variable and edit template image.
        if self.lastUpdate == 0:
            await self.editCovidImage(path, info)
            self.lastUpdate = info['tarih']
        # if latest date is not equal to lastupdate, it sends the information to the given guilds.
        elif info['tarih'] != self.lastUpdate:
            await self.editCovidImage(path, info)
            for guild in self.bot.guilds:
                if guild.id in self.channels.keys():
                    if self.channels[int(guild.id)] != "":
                        channel = self.bot.get_channel(int(self.channels[int(guild.id)]))
                        await channel.send(file=File(f'{self.imagesDir}/covidresult.png')) #!
            self.lastUpdate = info['tarih']

    @command()
    async def testCovid(self, ctx):
        await ctx.message.delete()
        await ctx.send(self.channels)
