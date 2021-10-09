import re
import discord, aiohttp, asyncio, json, sys
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command
from discord import Embed, File
from datetime import datetime
import datetime as dt
from PIL import Image, ImageFont, ImageDraw

class Rates(Cog):
    def __init__(self, bot):
        self.bot = bot
        if sys.platform == "linux":
            rpi_os = True
            self.imagesDir = "/home/pi/asbot/mecha/cogs/Images" #! 
            self.logDir = "/home/pi/asbot/mecha/cogs/Logs" #! 
            self.ratesLogDir = f'{self.logDir}/updates.json'
        else:
            rpi_os = False
            self.imagesDir = "C:/Dev/Github/src/mecha/cogs/Images"
            self.logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
            self.ratesLogDir = f'{self.logDir}\\updates.json'

        self.ratesLog = {} # * {guildId:{channel:----, message:----}, ...}
        self.get_rates_log()
        self.imagePaths = {'path':f'{self.imagesDir}/bloombergtable.png', 'down':f'{self.imagesDir}/down.png', 'up':f'{self.imagesDir}/up.png', 'notr':f'{self.imagesDir}/notr.png', 'font':f'{self.imagesDir}/futura-bold/futura-bold.otf', 'save':f'{self.imagesDir}/rates.png'}
    
    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.initialize_rates_guild(int(guild.id))

    def get_rates_log(self):
        with open(self.ratesLogDir) as ratesLogFile:
            data = json.load(ratesLogFile)
        for guildId in data.keys():
            self.ratesLog.update({int(guildId):{"channel":((data[guildId])["rates"])["channel"],"last_message":((data[guildId])["rates"])["last_message"]}})

    def update_rates_log(self, guildId, last_message=None, channel=None):
        with open(self.ratesLogDir) as ratesLogFile:
            data = json.load(ratesLogFile)
        if channel == None:
            ((data[str(guildId)])["rates"]).update({"last_message":last_message})
        elif last_message == None:
            ((data[str(guildId)])["rates"]).update({"channel":channel})
        else:
            return
        with open(self.ratesLogDir, "w") as ratesLogFile:
            json.dump(data, ratesLogFile)

    async def initialize_rates_guild(self, guildId):
        guild = self.bot.get_guild(id=int(guildId))
        try:
            chl = discord.utils.get(guild.text_channels, id=int((self.ratesLog[int(guildId)])['channel']))
            try:
                msg = await chl.fetch_message(id=int((self.ratesLog[int(guildId)])['last_message']))
                await msg.add_reaction('🔁')
            except:
                img = await self.editRatesImage()
                img.save(self.imagePaths['save'])
                msg = await chl.send(file=File(self.imagePaths['save']))
                await msg.add_reaction('🔁')
                (self.ratesLog[int(guildId)])['last_message'] = int(msg.id)
                self.update_rates_log(guildId, last_message=int(msg.id))
        except Exception as Err:
            print(f'Errorx3005: {Err}')

    @command()
    @commands.has_permissions(manage_channels=True)
    async def rateschannel(self, ctx, channelId=None):
        guild = ctx.guild
        await ctx.message.delete()
        if channelId != None:
            try:
                chl = discord.utils.get(guild.text_channels, id=int(channelId))
                self.update_rates_log(guild.id, channel=int(channelId))
                (self.ratesLog[int(guild.id)])["channel"] = int(channelId)
                await self.initialize_rates_guild(int(guild.id))
                await ctx.send("Kur kanalı başarılı bir şekilde belirlendi.")
            except Exception as Err:
                print(f'Errorx3006: {Err}')
                await ctx.send("İstek yerine getirilemedi, lütfen tekrar deneyiniz!")
                return

    async def editRatesImage(self):
        ratesData = await self.rates()
        img = Image.open(self.imagePaths['path'])
        imgdown = Image.open(self.imagePaths['down'])
        imgup = Image.open(self.imagePaths['up'])
        imgnotr = Image.open(self.imagePaths['notr'])
        titles = ["BIST100", "USD/TRY", "EUR/TRY", "ALTIN/ONS", "FAIZ", "BRENT"]
        image_editable = ImageDraw.Draw(img)
        font1 = ImageFont.truetype(self.imagePaths['font'], 200)
        font2 = ImageFont.truetype(self.imagePaths['font'], 100)
        font3 = ImageFont.truetype(self.imagePaths['font'], 150)

        x, y = 3925, 408
        for k in range(len(titles)):
            image_editable.text((x, y), str(ratesData[k]), (255, 255, 255), anchor="rt", font=font1, align="right")

            if ratesData[k+6] > 0:
                img.paste(imgup, (x-3727, y-138))
                image_editable.text((x-1275, y+70), f'%{str(ratesData[k+6])}', (255, 255, 255), anchor="rt", font=font3)
            elif ratesData[k+6] < 0:
                img.paste(imgdown, (x-3727, y-138))
                image_editable.text((x-1275, y+70), f'-%{str(abs(ratesData[k+6]))}', (255, 255, 255), anchor="rt", font=font3)
            else:
                img.paste(imgnotr, (x-3727, y-138))
                image_editable.text((x-1275, y+70), '%0.00', (255, 255, 255), anchor="rt", font=font3)
        
            y+=623
    
        time1 = ratesData[13]
        time1 = time1.replace(":", ".")
        image_editable.text((2765, 4005), time1, (255, 255, 255), font=font2) 
        return img

    async def rates(self):
        bloomberghturl = "https://www.bloomberght.com/"
        time1 = datetime.now()
        time1 += dt.timedelta(hours=3)
        time1 = time1.strftime("%H:%M:%S %d/%m/%Y")
        async with aiohttp.ClientSession() as session:
            async with session.get(bloomberghturl) as response:
                req = await response.text()
        bist100str = str(req[req.find('<li class="up live-bist-100">')+len('<li class="up live-bist-100">'):req.rfind('<li class="up live-dolar">')])
        bist100 = float((((((bist100str.split('data-secid="XU100 Index">'))[1]).split("<"))[0]).replace(".", "")).replace(",", "."))
        percBist = eval((((((bist100str.split('data-secid="XU100 Index"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", ".")).replace("%", ""))
        brentstr = str(req[req.find('<li class="up live-brent-petrol">')+len('<li class="up live-brent-petrol">'):req.rfind('<!--Ekonomi Verileri Finito-->')])
        brent = float((((((brentstr.split('data-secid="CO1 Comdty">'))[1]).split("<"))[0]).replace(".", "")).replace(",", "."))
        percBrent = eval((((((brentstr.split('data-secid="CO1 Comdty"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", ".")).replace("%", ""))
        dolarstr = str(req[req.find('<li class="up live-dolar">')+len('<li class="up live-dolar">'):req.rfind('<li class="up live-euro">')])
        dolar = str(req[req.find('data-secid="USDTRY Curncy">')+len('data-secid="USDTRY Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="USDTRY Curncy"')])
        dolar = float(((dolar.split("<"))[0].replace(".", "")).replace(",", "."))
        percDolar = eval((((((dolarstr.split('data-secid="USDTRY Curncy"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", ".")).replace("%", ""))
        eurostr = str(req[req.find('<li class="up live-euro">')+len('<li class="up live-euro">'):req.rfind('<li class="up live-eur-usd">')])
        euro = str(req[req.find('data-secid="EURTRY Curncy">')+len('data-secid="EURTRY Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="EURTRY Curncy"')])
        euro = float(((euro.split("<"))[0].replace(".", "")).replace(",", "."))
        percEuro = eval((((((eurostr.split('data-secid="EURTRY Curncy"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", ".")).replace("%", ""))
        onsstr = str(req[req.find('<li class="down live-altin-ons">')+len('<li class="down live-altin-ons">'):req.rfind('<li class="up live-brent-petrol">')])
        ons = str(req[req.find('data-secid="XAU Curncy">')+len('data-secid="XAU Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="XAU Curncy"')])
        ons = float((((ons.split("<"))[0]).replace(".", "")).replace(",", "."))
        percOns = eval((((((onsstr.split('data-secid="XAU Curncy"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", ".")).replace("%", ""))
        faizstr = str(req[req.find('<li class="round live-faiz">')+len('<li class="round live-faiz">'):req.rfind('<li class="down live-altin-ons">')])
        faiz = float((((((faizstr.split('data-secid="TAHVIL2Y">'))[1]).split("<"))[0]).replace(".", "")).replace(",", "."))
        percFaiz = eval(((((faizstr.split('data-secid="TAHVIL2Y"'))[3]).split('PercentChange">\n')[1]).split('</small>')[0]).replace(",", "."))
        picture = str(req[req.find('<link rel="apple-touch-icon" sizes="152x152" href="')+len('<link rel="apple-touch-icon" sizes="152x152" href="'):req.find('<link rel="apple-touch-icon" sizes="144x144" href="')])
        picture = (picture.split('"'))[0]

        return bist100, dolar, euro, ons, faiz, brent, percBist, percDolar, percEuro, percOns, percFaiz, percBrent, picture, time1

    @command(name='kur')
    async def kur(self, ctx):
        img = await self.editRatesImage()
        img.save(self.imagePaths['save'])
        await ctx.send(file=File(self.imagePaths['save']))

    async def fastRates(self):
        bloomberghturl = "https://www.bloomberght.com/"
        time1 = datetime.now()
        time1 += dt.timedelta(hours=3)
        time1 = time1.strftime("%H:%M:%S %d/%m/%Y")
        async with aiohttp.ClientSession() as session:
            async with session.get(bloomberghturl) as response:
                req = await response.text()
            async with session.get(f'{bloomberghturl}altin/') as response2:
                req2 = await response2.text()
        dolar = str(req[req.find('data-secid="USDTRY Curncy">')+len('data-secid="USDTRY Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="USDTRY Curncy"')])
        dolar = float(((dolar.split("<"))[0].replace(".", "")).replace(",", "."))
        euro = str(req[req.find('data-secid="EURTRY Curncy">')+len('data-secid="EURTRY Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="EURTRY Curncy"')])
        euro = float(((euro.split("<"))[0].replace(".", "")).replace(",", "."))
        ons = str(req[req.find('data-secid="XAU Curncy">')+len('data-secid="XAU Curncy">'):req.rfind('<small data-type="yuzde_degisim" data-secid="XAU Curncy"')])
        ons = float((((ons.split("<"))[0]).replace(".", "")).replace(",", "."))
        picture = str(req[req.find('<link rel="apple-touch-icon" sizes="152x152" href="')+len('<link rel="apple-touch-icon" sizes="152x152" href="'):req.find('<link rel="apple-touch-icon" sizes="144x144" href="')])
        picture = "https://www.bloomberght.com" + (picture.split('"'))[0]
        try:
            sellgram = str(req2[req2.find('<td><a title="" href="/altin/gram-altin"><i class="data-icon down"></i><span>ALIŞ(TL)</span></a></td>')+len('<td><a title="" href="/altin/gram-altin"><i class="data-icon down"></i><span>ALIŞ(TL)</span></a></td>'):req2.rfind('<td><a title="" href="/altin/gram-altin"><i class="data-icon down"></i><span>SATIŞ(TL)</span></a></td>')])
            sellgram = float((((((sellgram.split("<"))[1]).split(">"))[1]).replace(".", "")).replace(",", "."))
        except:
            sellgram = str(req2[req2.find('<td><a title="" href="/altin/gram-altin"><i class="data-icon up"></i><span>ALIŞ(TL)</span></a></td>')+len('<td><a title="" href="/altin/gram-altin"><i class="data-icon up"></i><span>ALIŞ(TL)</span></a></td>'):req2.rfind('<td><a title="" href="/altin/gram-altin"><i class="data-icon up"></i><span>SATIŞ(TL)</span></a></td>')])
            sellgram = float((((((sellgram.split("<"))[1]).split(">"))[1]).replace(".", "")).replace(",", "."))
        try:
            buygram = str(req2[req2.find('<td><a title="" href="/altin/gram-altin"><i class="data-icon down"></i><span>SATIŞ(TL)</span></a></td>')+len('<td><a title="" href="/altin/gram-altin"><i class="data-icon down"></i><span>SATIŞ(TL)</span></a></td>'):req2.rfind('<td><a title="" href="/altin/ceyrek-altin"><i class="data-icon down"></i><span>ALIŞ(TL)</span></a></td>')])
            buygram = float((((((buygram.split("<"))[1]).split(">"))[1]).replace(".", "")).replace(",", "."))
        except:
            buygram = str(req2[req2.find('<td><a title="" href="/altin/gram-altin"><i class="data-icon up"></i><span>SATIŞ(TL)</span></a></td>')+len('<td><a title="" href="/altin/gram-altin"><i class="data-icon up"></i><span>SATIŞ(TL)</span></a></td>'):req2.rfind('<td><a title="" href="/altin/ceyrek-altin"><i class="data-icon up"></i><span>ALIŞ(TL)</span></a></td>')])
            buygram = float((((((buygram.split("<"))[1]).split(">"))[1]).replace(".", "")).replace(",", "."))
        return dolar, euro, ons, picture, sellgram, buygram, time1

    @command()
    async def fastKur(self, ctx):
        dolar, euro, ons, picture, sellgram, buygram, time1 = await self.fastRates()
        try:
            text1 = f'💵 - Dolar: {dolar}\n💶 - Euro: {euro}\n:coin: - Ons: {ons}'
            text2 = f':regional_indicator_s: - Gram Altın Satış: {sellgram}\n:regional_indicator_a: - Gram Altın Alış: {buygram}'
            embed = Embed(title='💰 - KURLAR - 💰', color=0xffff00)
            embed.add_field(name='Doviz', value=text1, inline=False)
            embed.add_field(name='Gram Altın', value=text2, inline=False)
            embed.set_thumbnail(url=picture)
            embed.add_field(name="\u200b", value=f':smirk: • {time1}')
            await ctx.send(embed=embed)
        except:
            print("ERROR! Rates.")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        refresh = '🔁'
        if str(payload.emoji) != refresh:
            return
        if payload.member.bot:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if payload.guild_id in self.ratesLog.keys():
            if payload.message_id == (self.ratesLog[int(payload.guild_id)])['last_message']:
                try:
                    chl = discord.utils.get(guild.text_channels, id=int((self.ratesLog[int(payload.guild_id)])['channel']))
                    msg = await chl.fetch_message(id=int((self.ratesLog[int(payload.guild_id)])['last_message']))
                    img = await self.editRatesImage()
                    img.save(self.imagePaths['save'])
                    await msg.delete()
                    msg = await chl.send(file=File(self.imagePaths['save']))
                    await msg.add_reaction('🔁')
                    (self.ratesLog[int(payload.guild_id)])['last_message'] = int(msg.id)
                    self.update_rates_log(payload.guild_id, last_message=int(msg.id))
                except Exception as Err:
                    print(f'Errorx3099: {Err}')

    @command()
    async def testRates(self, ctx):
        await ctx.message.delete()
        await ctx.send(self.ratesLog)
