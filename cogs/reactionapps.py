from math import e
from os import name
import re
from discord import message, team
from discord.embeds import Embed
from discord.partial_emoji import PartialEmoji
from discord.ext.commands import Cog, command
from discord.ext import commands
import datetime, discord, json, sys

class ReactionApplications(Cog):
    def __init__(self, bot, console):
        self.bot = bot
        self.console = console
        if sys.platform == "linux":
            rpi_os = True
            self.logDir = "/home/pi/asbot/Logs" #! 
            self.appsLogDir = f'{self.logDir}/reactionapps.json'
            self.adminLogDir = f'{self.logDir}/admin.json'
        else:
            rpi_os = False
            self.logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
            self.appsLogDir = f'{self.logDir}\\reactionapps.json'
            self.adminLogDir = f'{self.logDir}\\admin.json'
        self.roleApplications = {} # * {guildId:{channelId:{messageId:{emojiID1:roleID1, emojiID2:roleID2, ...}, ...}, ...}, ...}
        self.chanellPermApplications = {} # * {guildId:{channelId:{messageId:{emojiID1:channelID1, emojiID2:channelID2, ...}, ...}, ...}, ...}

    @Cog.listener()
    async def on_ready(self):
        self.get_applications()
        await self.console.print_console(level=2, number="6001", logText=f'Reaction Applications has been taken.')
        botGuilds = list(int(guild.id) for guild in self.bot.guilds)
        for guildId in self.roleApplications.keys():
            if int(guildId) in botGuilds:
                await self.initialize_apps(guildId)
        for guildId in self.chanellPermApplications.keys():
            if int(guildId) in botGuilds:
                await self.initialize_apps(guildId, appType="channelPerm")
        await self.console.print_console(level=2, number="6002", logText=f'Reaction Applications Class has been started.')

    async def add_emoji_to_message(self, guildId, channelId, messageId, emoji, add_emoji=True):
        guild = self.bot.get_guild(id=int(guildId))
        chl = discord.utils.get(guild.text_channels, id=int(channelId))
        msg = await chl.fetch_message(id=int(messageId))
        try:
            emoji = self.bot.get_emoji(id=int(emoji))
        except:
            return
        if add_emoji == True:
            await msg.add_reaction(emoji)
        else:
            await msg.remove_reaction(emoji, guild.me)

    async def initialize_apps(self, guildId, appType="role"):
        if appType == "role":
            logs = self.roleApplications[int(guildId)]
        else:
            logs = self.chanellPermApplications[int(guildId)]
        guild = self.bot.get_guild(id=int(guildId))
        for chlId in logs.keys():
            for msgId in (logs[chlId]).keys():
                for emj in ((logs[chlId])[msgId]).keys():
                    try:
                        await self.add_emoji_to_message(guildId, chlId, msgId, emj)
                    except Exception as Err:
                        print(f'Errorx____: {Err}')

    def get_applications(self):
        with open(self.appsLogDir) as appsLogFile:
            data = json.load(appsLogFile)
        for guildId in data["role"].keys():
            self.roleApplications.update({int(guildId):(data["role"])[guildId]})
        for guildId in data["channel_permissions"].keys():
            self.chanellPermApplications.update({int(guildId):(data["channel_permissions"])[guildId]})

    def update_log_all(self, appType, guildId):
        with open(self.appsLogDir) as appsLogFile:
            data = json.load(appsLogFile)
        if appType == "role":
            log = self.roleApplications[int(guildId)]
        elif appType == "channel_permissions":
            log = self.chanellPermApplications[int(guildId)]
        else:
            return
        (data[str(appType)]).update({str(guildId):log})
        with open(self.appsLogDir, "w") as appsLogFile:
            json.dump(data, appsLogFile)

    def update_log(self, guildId, channelId, messageId, emoji, roleId=None, targetChannelId=None):
        if roleId == None:
            logs = self.chanellPermApplications
            target = targetChannelId
        elif targetChannelId == None:
            logs = self.roleApplications
            target = roleId
        else:
            return 0
        if int(guildId) in logs.keys():
            if str(channelId) in (logs[int(guildId)]).keys():
                if str(messageId) in ((logs[int(guildId)])[str(channelId)]).keys():
                    if str(emoji) in (((logs[int(guildId)])[str(channelId)])[str(messageId)]).keys():
                        return -1
                    (((logs[int(guildId)])[str(channelId)])[str(messageId)]).update({str(emoji):int(target)})
                else:
                    ((logs[int(guildId)])[str(channelId)]).update({str(messageId):{str(emoji):int(target)}})
            else:
                (logs[int(guildId)]).update({str(channelId):{str(messageId):{str(emoji):int(target)}}})
        else:
            logs.update({int(guildId):{str(channelId):{str(messageId):{str(emoji):int(target)}}}})
        
        with open(self.appsLogDir) as appsLogFile:
            data = json.load(appsLogFile)

        if roleId == None:
            self.chanellPermApplications = logs
            data.update({"channel_permissions":logs})
        elif targetChannelId == None:
            self.roleApplications = logs
            data.update({"role":logs})
        with open(self.appsLogDir, "w") as appsLogFile:
            json.dump(data, appsLogFile)

    @command()
    async def listapps(self, ctx, appType="all"):
        guild = ctx.guild
        if appType == "all":
            if int(guild.id) in self.roleApplications.keys() and int(guild.id) in self.chanellPermApplications.keys():
                data = {"role":self.roleApplications[int(guild.id)], "channel_perm":self.chanellPermApplications[int(guild.id)]}
            elif int(guild.id) in self.roleApplications.keys():
                data = {"role":self.roleApplications[int(guild.id)]}
            elif int(guild.id) in self.chanellPermApplications.keys():
                data = {"channel_perm":self.chanellPermApplications[int(guild.id)]}
            else:
                await ctx.send("Sunucuda herhangi bir uygulama bulunmuyor.")
                return
        elif appType == "role":
            if int(guild.id) in self.roleApplications.keys():
                data = {"role":self.roleApplications[int(guild.id)]}
            else:
                await ctx.send("Sunucuda herhangi bir uygulama bulunmuyor.")
                return
        elif appType == "channel":
            if int(guild.id) in self.chanellPermApplications.keys():
                data = {"channel_perm":self.chanellPermApplications[int(guild.id)]}
            else:
                await ctx.send("Sunucuda herhangi bir uygulama bulunmuyor.")
                return
        else:
            await ctx.send("??ste??iniz ger??ekle??tirilemedi, tekrar deneyiniz!")
            return
        for item in data.keys():
            cnt = f'```diff\n- SUNUCUDAK?? REACTION UYGULAMALARI - {(str(item)).upper()}: \n'
            count = 1
            cnts = []
            for chl in data[item].keys():
                for msg in ((data[item])[chl]).keys():
                    for emj in (((data[item])[chl])[msg]).keys():
                        cnt += f'{str(count)} - Kanal Id: {str(chl)} / Mesaj Id: {str(msg)} / Emoji: {str(emj)}\n'
                        count += 1
                        if len(cnt) > 1950:
                            cnt += "```"
                            cnts.append(cnt)
                            cnt = f'```diff\n- SUNUCUDAK?? REACTION UYGULAMALARI - {(str(item)).upper()} (CONTINUED): \n'
            cnt+="```"
            cnts.append(cnt)
            for c in cnts:
                await ctx.send(c)

    @command()
    async def addapp(self, ctx, appType="role", msgid=None, emojiStr=None, targetId=None):
        if msgid == None or emojiStr == None or targetId == None:
            await ctx.send("Eksik bilgi girdiniz!")
            return
        guild = ctx.guild
        for chl in guild.text_channels:
            try:
                msg = await chl.fetch_message(id=int(msgid))
                break
            except:
                msg = None
        if msg == None:
            await ctx.send("Mesaj bulunamad??!")
            return
        try:
            emojiId = emojiStr
            emojiId = ((((str(emojiId)).split(":"))[2]).split(">"))[0]
            emoji = self.bot.get_emoji(id=int(emojiId))
        except:
            emojiId = None
            emoji = PartialEmoji(name=emojiStr)
            if emoji == None:
                await ctx.send("Emoji bulunamad??!")
                return
        appCount = 0
        if int(guild.id) in self.roleApplications.keys():
            if str(chl.id) in (self.roleApplications[int(guild.id)]).keys():
                if str(msgid) in ((self.roleApplications[int(guild.id)])[str(chl.id)]).keys():
                    appCount += len((((self.roleApplications[int(guild.id)])[str(chl.id)])[str(msgid)]).keys())
        if int(guild.id) in self.chanellPermApplications.keys():
            if str(chl.id) in (self.chanellPermApplications[int(guild.id)]).keys():
                if str(msgid) in ((self.chanellPermApplications[int(guild.id)])[str(chl.id)]).keys():
                    appCount += len((((self.chanellPermApplications[int(guild.id)])[str(chl.id)])[str(msgid)]).keys())
        if appCount >= 20:
            await ctx.send("Uygulama olu??turulamad??. Se??ilen mesaj i??in maksimum emoji say??s??na ula????lm????t??r.")
            return
        if str(appType).lower() == "role":
            for r in guild.roles:
                if int(r.id) == int(targetId):
                    role = r
                    break
                else:
                    role = None
            if role == None:
                await ctx.send("Rol bulunamad??!")
                return
            if emojiId == None:
                self.update_log(guild.id, chl.id, msgid, str(emoji), roleId=targetId)
            else:
                self.update_log(guild.id, chl.id, msgid, str(emojiId), roleId=targetId)
        elif str(appType).lower() == "channel":
            try:
                targetChannel = discord.utils.get(guild.text_channels, id=int(targetId))
            except Exception as Err:
                print(f'Errorx6010: {Err}')
                await ctx.send("Hedef kanal bulunamad??!")
                return
            if emojiId == None:
                self.update_log(guild.id, chl.id, msgid, str(emoji), targetChannelId=targetId)
            else:
                self.update_log(guild.id, chl.id, msgid, str(emojiId), targetChannelId=targetId)
        else:
            await ctx.send("Se??ilen uygulama bulunamad??!")
            return
        await ctx.send("**Uygulama olu??turuldu.**")
        await msg.add_reaction(emoji)
        await ctx.message.delete()

    @command()
    async def removeapp(self, ctx, appType=None, order=None):
        guild = ctx.guild
        if str(appType).lower() == "all":
            if int(guild.id) in self.roleApplications.keys():
                self.roleApplications.update({int(guild.id):{}})
                self.update_log_all(appType="role", guildId=int(guild.id))
            if int(guild.id) in self.chanellPermApplications.keys():
                self.chanellPermApplications.update({int(guild.id):{}})
                self.update_log_all(appType="channel_permissions", guildId=int(guild.id))
            await ctx.send("Sunucu ile ilgili t??m uygulamalar silindi!")
            return
        elif str(appType).lower() == "role":
            delete_category = "role"
            if not int(guild.id) in self.roleApplications.keys():
                await ctx.send("Sunucuya ait bilgi bulunamad??!")
                return
        elif str(appType).lower() == "channel":
            delete_category = "channel_permissions"
            if not int(guild.id) in self.chanellPermApplications.keys():
                await ctx.send("Sunucuya ait bilgi bulunamad??!")
                return
        else:
            await ctx.send("Kategori bulunamad??!")
            return
        
        if delete_category == "role":
            if str(order).lower() == "all":
                self.roleApplications.update({int(guild.id):{}})
                await ctx.send('Sunucudaki role uygulamalar?? silindi.')
                self.update_log_all(appType="role", guildId=int(guild.id))
            else:
                try:
                    count = 1
                    for chl in (self.roleApplications[int(guild.id)]).keys():
                        for msg in ((self.roleApplications[int(guild.id)])[chl]).keys():
                            for emj in (((self.roleApplications[int(guild.id)])[chl])[msg]).keys():
                                if count == int(order):
                                    (((self.roleApplications[int(guild.id)])[chl])[msg]).pop(emj, None)
                                    await ctx.send(f'{str(count)} s??radaki uygulama silindi.')
                                    self.update_log_all(appType="role", guildId=int(guild.id))
                                    return
                                count += 1
                except Exception as Err:
                    print(f'Errorx6020: {Err}')
        elif delete_category == "channel_permissions":
            if str(order).lower() == "all":
                self.chanellPermApplications.update({int(guild.id):{}})
                await ctx.send('Sunucudaki channel uygulamalar?? silindi.')
                self.update_log_all(appType="channel_permissions", guildId=int(guild.id))
            else:
                try:
                    count = 1
                    for chl in (self.chanellPermApplications[int(guild.id)]).keys():
                        for msg in ((self.chanellPermApplications[int(guild.id)])[chl]).keys():
                            for emj in (((self.chanellPermApplications[int(guild.id)])[chl])[msg]).keys():
                                if count == int(order):
                                    (((self.chanellPermApplications[int(guild.id)])[chl])[msg]).pop(emj, None)
                                    await ctx.send(f'{str(count)} s??radaki uygulama silindi.')
                                    self.update_log_all(appType="channel_permissions", guildId=int(guild.id))
                                    return
                                count += 1
                except Exception as Err:
                    print(f'Errorx6021: {Err}')        
        await ctx.message.delete()

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            if payload.member.bot:
                return
        except:
            return
        guild = self.bot.get_guild(id=int(payload.guild_id))
        
        if int(payload.guild_id) in self.chanellPermApplications.keys() or int(payload.guild_id) in self.roleApplications.keys():
            # Channel Permission Reaction Check
            try:
                if str(payload.channel_id) in (self.chanellPermApplications[int(payload.guild_id)]).keys():
                    if str(payload.message_id) in ((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)]).keys():
                        try:
                            targetChannelId = (((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji.id)]
                        except:
                            targetChannelId = (((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji)]
                        targetChannel = discord.utils.get(guild.text_channels, id=int(targetChannelId))
                        user = discord.utils.get(guild.members, id=int(payload.user_id))
                        try:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = True
                            overwrite.send_messages = True
                            overwrite.read_messages = True
                            overwrite.read_message_history = True
                            await targetChannel.set_permissions(user, overwrite=overwrite)
                        except Exception as Err:
                            await self.console.print_console(level=4, number="6031", logText=f'Reaction Application - Reaction add at {str(payload.guild_id)} in the message {str(payload.message_id)} and emoji {str(payload.emoji)} - {Err}')
                            print('Errorx6031: ' + str(Err))
            except:
                pass
            # Take Role Reaction Check
            try:
                if str(payload.channel_id) in (self.roleApplications[int(payload.guild_id)]).keys():
                    if str(payload.message_id) in ((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)]).keys():
                        try:
                            roleId = (((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji.id)]
                        except:
                            roleId = (((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji)]
                        role = guild.get_role(int(roleId))
                        user = discord.utils.get(guild.members, id=int(payload.user_id))
                        try:
                            await user.add_roles(role)
                        except Exception as Err:
                            await self.console.print_console(level=4, number="6032", logText=f'Reaction Application - Reaction add at {str(payload.guild_id)} in the message {str(payload.message_id)} and emoji {str(payload.emoji)} - {Err}')
                            print('Errorx6032: ' + str(Err))
            except:
                pass

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(id=int(payload.guild_id))
        try:
            if payload.member.bot:
                return
        except:
            user = discord.utils.get(guild.members, id=int(payload.user_id))
            if user.bot:
                return
        else:
            print("Errorx6041")
        
        if int(payload.guild_id) in self.chanellPermApplications.keys() or int(payload.guild_id) in self.roleApplications.keys():
            try:    
                if str(payload.channel_id) in (self.chanellPermApplications[int(payload.guild_id)]).keys():
                    if str(payload.message_id) in ((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)]).keys():
                    # Take Back Channel Permission Check
                        try:
                            targetChannelId = (((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji.id)]
                        except:
                            targetChannelId = (((self.chanellPermApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji)]
                        targetChannel = discord.utils.get(guild.text_channels, id=int(targetChannelId))
                        user = discord.utils.get(guild.members, id=int(payload.user_id))
                        try:
                            await targetChannel.set_permissions(user, overwrite=None)
                        except Exception as Err:
                            await self.console.print_console(level=4, number="6042", logText=f'Reaction Application - Reaction remove at {str(payload.guild_id)} in the message {str(payload.message_id)} and emoji {str(payload.emoji)} - {Err}')
                            print('Errorx6042: ' + str(Err))
            except:
                pass
            try:
                if str(payload.channel_id) in (self.roleApplications[int(payload.guild_id)]).keys():
                    if str(payload.message_id) in ((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)]).keys():
                        # Remove Role Reaction Check
                        try:
                            roleId = (((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji.id)]
                        except:
                            roleId = (((self.roleApplications[int(payload.guild_id)])[str(payload.channel_id)])[str(payload.message_id)])[str(payload.emoji)]
                        role = guild.get_role(int(roleId))
                        user = discord.utils.get(guild.members, id=int(payload.user_id))
                        try:
                            await user.remove_roles(role)
                        except Exception as Err:
                            await self.console.print_console(level=4, number="6043", logText=f'Reaction Application - Reaction remove at {str(payload.guild_id)} in the message {str(payload.message_id)} and emoji {str(payload.emoji)} - {Err}')
                            print('Errorx6043: ' + str(Err))
            except:
                pass

    @command()
    async def reactionapps(self, ctx):
        texts = [
            'Mecha Bot Tepki ile Rol Verme Veya Kanal i??in ??zin verme',
            'A????klama:',
            '-Tepki ekleyerek ??yelere kanal g??rme veya rol verme ??zelli??i eklemek i??in ??ncelikle herhangi bir kanala (moderasyon kanal?? olmas?? ??nerilir.) i??levleri belirtecek birer mesaj at??lmal??d??r. Bir tane rol ile tepki bilgisi i??in bir tane de tepki ile kanal g??rme bilgisi i??in mesaj at??lacakt??r. Mesajlar??n bulundu??u kanal??n idsi ve mesajlar??n idleri yetkiliye bildirilmelidir.',
            '-Yetkili mesaj bilgilerini bota ekledikten sonra mesaj?? d??zenleyerek yeni i??levler ekleyebilir veya ????karabilirsiniz. E??er mesajda bir format yanl????l?????? varsa bot mesaja :x: ekleyecektir. S??k??nt?? yoksa :white_check_mark: ekleyecektir. Yanl????l??k oldu??unda d??zeltmeniz gerekmektedir.',
            'Mesaj Formatlar??: ',
            "+ Kanal i??in ??zin Verme ????levleri Bilgisi:\n[\n[mesaj??nBulundu??uKanal??nIDsi1, mesaj??nIDsi1, ':sunglasses:', ki??ininEklenece??iKanal??nIdsi1],\n[mesaj??nBulundu??uKanal??nIDsi2, mesaj??nIDsi2, ':smile:', ki??ininEklenece??iKanal??nIdsi2]\n]",
            "+ Rol Verme ????levleri Bilgisi:\n[\n[mesaj??nBulundu??uKanal??nIDsi1, mesaj??nIDsi1, ':sunglasses:', ki??iyeEklenecekRol??nIDsi1],\n[mesaj??nBulundu??uKanal??nIDsi2, mesaj??nIDsi2, ':smile:', ki??iyeEklenecekRol??nIDsi2]\n]",
            "Not:",
            "1- Format basit liste i??inde listelerden olu??mal??d??r. \n  2- Emoji ba????na ve sonuna ' i??areti konulmal??d??r.\n  3- IDler say?? olmal??d??r.\n  4- Her bir i??lev aras??na , konmal??d??r."]
        embed = Embed(title=texts[0], color=0x1abc9c)
        embed.add_field(name=texts[1], value=f'{texts[2]}\n{texts[3]}', inline=False)
        embed.add_field(name=texts[4], value=f'{texts[5]}\n{texts[6]}', inline=False)
        embed.add_field(name=texts[7], value=texts[8], inline=False)
        try:
            embed.set_image(url='https://cdn.discordapp.com/attachments/783396105907077160/844651127319691304/reactionappslogs.png')
        except:
            pass
        await ctx.send(embed=embed)

    @command()
    async def testApp(self, ctx, emj=None):
        await ctx.message.delete()
        #emj = PartialEmoji(name=emj)
        #await ctx.send(emj)
        #print(emj.is_unicode_emoji(), emj.id)
        #emj = ((((str(emj)).split(":"))[2]).split(">"))[0]
        #print(emj)
        print(self.roleApplications)