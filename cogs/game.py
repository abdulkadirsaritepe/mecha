
from functools import partial
from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import Embed, channel, File
import time, discord, sys
import random
from PIL import Image, ImageFont, ImageDraw

class StonePaperScissor(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = {'stone':'🗿', 'paper':'📄', 'scissor':'✂'}
        self.active_games = {}

    @command()
    async def tkm(self, ctx):
        guild = ctx.guild
        game_msg = await ctx.send('🤜\t🤛')
        await ctx.message.delete()
        for item in self.emojis.keys():
            await game_msg.add_reaction(self.emojis[item])
        if int(guild.id) in self.active_games.keys():
            if int(game_msg.channel.id) in (self.active_games[int(guild.id)]).keys():
                oldData = (self.active_games[int(guild.id)])[int(game_msg.channel.id)]
                oldData.append(int(game_msg.id))
                (self.active_games[int(guild.id)])[int(game_msg.channel.id)] = oldData
            else:
                (self.active_games[int(guild.id)]).update({int(game_msg.channel.id):[int(game_msg.id)]})
        else:
            self.active_games.update({int(guild.id):{int(game_msg.channel.id):[int(game_msg.id)]}})

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            if payload.member.bot:
                return
        except:
            return
        guild = self.bot.get_guild(id=int(payload.guild_id))
        if not str(payload.emoji) in self.emojis.values():
            return
        if int(payload.guild_id) in self.active_games.keys():
            if int(payload.message_id) in ((self.active_games[int(payload.guild_id)])[int(payload.channel_id)]):
                ctx = discord.utils.get(guild.text_channels, id=int(payload.channel_id))
                bot_choice = random.choice(list(self.emojis.values()))
                user_choice = str(payload.emoji)
                if bot_choice == user_choice:
                    await ctx.send(f'**--Berabere--**\n{user_choice} X {bot_choice}')
                elif (user_choice == self.emojis['scissor'] and bot_choice == self.emojis['paper']) or (user_choice == self.emojis['stone'] and bot_choice == self.emojis['scissor']) or (user_choice == self.emojis['paper'] and bot_choice == self.emojis['stone']):
                    await ctx.send(f'**Kazandınız!**\n{user_choice} X {bot_choice}')
                else:
                    await ctx.send(f'**Kaybettiniz.**\n{user_choice} X {bot_choice}')
                ((self.active_games[int(payload.guild_id)])[int(payload.channel_id)]).remove(int(payload.message_id))


    @command()
    async def testTKM(self, ctx):
        print(self.active_games)

class FlipCoin(Cog):
    def __init__(self, bot):
        self.bot = bot
        if sys.platform == "linux":
            rpi_os = True
            self.imagesDir = "/home/pi/asbot/cogs/Images"
        else:
            rpi_os = False
            self.imagesDir = "C:/Dev/Github/src/mekanik/cogs/Images"
        self.coin_side_files = [f'{self.imagesDir}/1TL_obverse.png', f'{self.imagesDir}/1TL_reverse.png']

    @command(name='yazıtura')
    async def yazitura(self, ctx, times=1):
        if times == 1:
            result = random.choice(self.coin_side_files)
        elif times < 1:
            await ctx.send('Yeniden deneyiniz!')
            return
        else:
            img = Image.new('RGBA', (times*100, 100), (0,0,0,0))
            img_editable = ImageDraw.Draw(img)
            for t in range(times):
                side = random.choice(self.coin_side_files)
                
        await ctx.send(file=File(result))
        await ctx.message.delete()
