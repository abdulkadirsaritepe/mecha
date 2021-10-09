
from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import Embed
import time, discord, random

class Team(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainchannel = None
        self.subchannels = []
        self.teams = {}
        self.helpmsg = '```diff\n-TAKIM OLUŞTURMA\n\n+Ana kanalı seçme: &setmainchannel "channel id"\n\n+Alt kanalları seçme: &setsubchannels ["channel id1","channel id2",...]\n\n+Alt kanallara kanal ekleme: &addsubchannel "channel id"\n\n+Alt kanallara dağıtma: &seperate (Not: Takımlara ayırmada default olarak her seferinde ayrı takım oluşturuluyor, eğer aynı takımlar isteniliyorsa "&seperate same" yazabilirsiniz.)\n\n+Kişileri geri çağırma: &callback\n\n+Seçilenleri sıfırlama: &teamreset```'

    @command(name="team")
    @commands.has_permissions(manage_messages=True)
    async def info(self, ctx):
        await ctx.send(self.helpmsg)

    @command(name="setmainchannel")
    @commands.has_permissions(manage_messages=True)
    async def setmainchannel(self, ctx, channel):
        guild = ctx.guild
        self.mainchannel = discord.utils.get(guild.voice_channels, id=int(channel))
        print(self.mainchannel)
    
    @command(name="setsubchannels")
    @commands.has_permissions(manage_messages=True)
    async def setsubchannels(self, ctx, channels):
        guild = ctx.guild
        channels = eval(channels)
        for c in channels:
            try:
                chn = discord.utils.get(guild.voice_channels, id=int(c))
                self.subchannels.append(chn)
            except:
                await ctx.send(f'{c} kanalı bulunamadı.')
        print(self.subchannels)

    @command(name="addsubchannel")
    @commands.has_permissions(manage_messages=True)
    async def addsubchannel(self, ctx, channel):
        guild = ctx.guild
        try:
            chn = discord.utils.get(guild.voice_channels, id=int(channel))
            self.subchannels.append(chn)
        except:
            await ctx.send(f'{c} kanalı bulunamadı.')
        print(self.subchannels)  

    @command(name="seperate")
    @commands.has_permissions(manage_messages=True)
    async def seperate(self, ctx, how="random"):
        print(how)
        guild = ctx.guild
        mc = self.mainchannel
        sc = self.subchannels
        if how == "random":
            self.teams = {}
            capacities = {}
            for c in sc:
                capacities.update({c:0})

            for member in mc.members:
                done = False
                while not done:
                    randomchannel = random.choice(sc)
                    if capacities[randomchannel] < 5:
                        done = True
                await member.move_to(randomchannel)
                try:
                    members = self.teams[randomchannel]
                    members.append(member)
                except:
                    members = [member]
                self.teams.update({randomchannel:members})
        elif how == "same":
            if len(self.teams.keys()) > 0:
                for team in self.teams.keys():
                    for member in self.teams[team]:
                        await member.move_to(team)

    @command(name="callback")
    @commands.has_permissions(manage_messages=True)
    async def callback(self, ctx):
        guild = ctx.guild
        mc = self.mainchannel
        sc = self.subchannels
        for channel in sc:
            for member in channel.members:
                await member.move_to(mc)

    @command(name="teamreset")
    @commands.has_permissions(manage_messages=True)
    async def teamreset(self, ctx):
        self.mainchannel = None
        self.subchannels = []
        await ctx.send("Ayarlar sıfırlandı.")
