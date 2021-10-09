import discord, aiohttp, asyncio
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command
from discord import Embed
from datetime import datetime
import datetime as dt

class Rates2(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def rates(self):
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

    @command(name='kur2')
    async def kur2(self, ctx):
        dolar, euro, ons, picture, sellgram, buygram, time1 = await self.rates()
        try:
            text1 = f'Dolar: {dolar}\nEuro: {euro}\nOns: {ons}'
            text2 = f'Gram Altın Satış: {sellgram}\nGram Altın Alış: {buygram}'
            embed = Embed(color=0xffff00)
            embed.add_field(name='Kurlar', value=text1, inline=False)
            embed.add_field(name='Gram Altın', value=text2, inline=False)
            embed.set_thumbnail(url=picture)
            embed.add_field(name="\u200b", value=time1)
            await ctx.send(embed=embed)
        except:
            print("ERROR! Rates.")
            
class Covid2(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def covid19(self):
        bloomberghturl = "https://covid19.saglik.gov.tr/"
        async with aiohttp.ClientSession() as session:
            async with session.get(bloomberghturl) as response:
                req = await response.text()
        info = (req.split("var sondurumjson = "))[1]
        info = (eval((info.split(";//"))[0]))[0]
        # * Parameters = tarih, gunluk_test, gunluk_vaka, gunluk_hasta, gunluk_vefat, gunluk_iyilesen, toplam_test, toplam_hasta, toplam_vefat, toplam_iyilesen, toplam_yogun_bakim,
        # * toplam_entube, hastalarda_zaturre_oran, agir_hasta_sayisi, yatak_doluluk_orani, eriskin_yogun_bakim_doluluk_orani, ventilator_doluluk_orani, 
        # * ortalama_filyasyon_suresi, ortalama_temasli_tespit_suresi, filyasyon_orani
        return info
    
    @command(name='covid2')
    async def covid2(self, ctx):
        info = await self.covid19()
        picture = "https://saglik.gov.tr/images/favicon/favicon-96x96.png"
        try:
            bugun = f'**-Test Sayısı:** {info["gunluk_test"]}\n**-Vaka Sayısı:** {info["gunluk_vaka"]}\n**-Hasta Sayısı:** {info["gunluk_hasta"]}\n**-Vefat Sayısı:** {info["gunluk_vefat"]}\n**-İyileşen Hasta Sayısı:** {info["gunluk_iyilesen"]}'
            toplam = f'**-Test Sayısı:** {info["toplam_test"]}\n**-Hasta Sayısı:** {info["toplam_hasta"]}\n**-Vefat Sayısı:** {info["toplam_vefat"]}\n**-Ağır Hasta Sayısı:** {info["agir_hasta_sayisi"]}\n**-İyileşen Hasta Sayısı:** {info["toplam_iyilesen"]}'
            embed = Embed(color=0xffff00, title="**T.C. Sağlık Bakanlığı Kovid Verileri**")
            embed.add_field(name='Bugün', value=bugun, inline=False)
            embed.add_field(name='Toplam', value=toplam, inline=False)
            embed.set_thumbnail(url=picture)
            embed.add_field(name="\u200b", value=f'**{info["tarih"]}**')
            await ctx.send(embed=embed)
        except:
            print("ERROR! Covid.")
