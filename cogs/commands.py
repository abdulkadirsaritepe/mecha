
from math import log
from re import T
from discord.enums import _is_descriptor
from discord.ext.commands import Cog, command
from discord.ext import commands, tasks
from discord import Embed, channel
from threading import Thread
import time, discord, json, sys
import texttable

from cogs.rpi import RPi

class Commands(Cog):
    def __init__(self, bot, bot_name, console):
        self.bot = bot
        self.bot_name = str(bot_name).lower()
        if sys.platform == "linux":
            self.rpi_os = True
            self.logDir = "/home/pi/asbot/mecha/cogs/Logs" #! 
            self.commandLogDir = f'{self.logDir}/commands.json'
            self.adminLogDir = f'{self.logDir}/admin.json'
        else:
            self.rpi_os = False
            self.logDir = "C:\Dev\Github\src\mecha\cogs\Logs"
            self.commandLogDir = f'{self.logDir}\commands.json'
            self.adminLogDir = f'{self.logDir}\\admin.json'
        self.console = console
        self.botResponds = {} # * {guildId:{userMessage:botRespond}, ...}
        self.botResponds2 = {} # * {guildId:{userMessage:botRespond}, ...}
        self.filterSettings = {}
        self.logs = {}
        self.doorStatusNotificationChannelId = None
        self.rpi = RPi()

    @Cog.listener()
    async def on_ready(self):
        with open(self.commandLogDir) as logs_file:
            self.logs = json.load(logs_file)
        await self.initializeLog("public")
        for guild in self.bot.guilds:
            await self.initializeLog(int(guild.id))
        await self.initializeDoorLog(743711488220594217) # TODO 743711488220594217 699224778824745003
        await self.console.print_console(level=2, number="0001", logText=f'Commands Class has been started.')
        if self.rpi_os:
            self.door_check.start()

    async def initializeLog(self, guildId):
        if guildId != "public":
            try:
                self.bot.get_guild(int(guildId))
            except Exception as Err:
                await self.console.print_console(level=4, number="1000", logText=f'{Err} raised at Commands/initializeLog.')
                print(f'Errorx1000: {Err}')
                return
            try:
                self.botResponds.update({int(guildId):dict((self.logs[str(guildId)])["botResponds"])})
                self.botResponds2.update({int(guildId):dict((self.logs[str(guildId)])["botResponds2"])})
                await self.console.print_console(level=2, number="1001", logText=f"Bot responds for guild {guildId} have been initialized.")
            except Exception as Err:
                await self.console.print_console(level=3, number="1002", logText=f'There is no info about guild {guildId} - Commands/initializeLog.')
                print(f'Errorx1002: {Err}')
                pass # TODO Add "guildId" keyword to the JSON file.
        else:
            try:
                self.botResponds.update({str(guildId):dict((self.logs[str(guildId)])["botResponds"])})
                self.botResponds2.update({str(guildId):dict((self.logs[str(guildId)])["botResponds2"])})
                await self.console.print_console(level=2, number="1003", logText="Public bot responds have been initialized.")
            except Exception as Err:
                await self.console.print_console(level=4, number="1004", logText=f'{Err} raised at Commands/initializeLog.')
                print(f'Errorx1004: {Err}')
                pass # TODO Add "public" keyword to the JSON file.

    async def updateLog(self, guildId, keyword1, keyword2=None, value2=None):
        with open(self.commandLogDir) as logs_file:
            self.logs = json.load(logs_file)
        if not str(guildId) in self.logs.keys():
            self.logs.update({str(guildId):{keyword1:value2}})
        elif keyword2 == None:
            (self.logs[str(guildId)]).update({keyword1:value2})
        else:
            ((self.logs[str(guildId)])[str(keyword1)]).update({keyword2:value2})
        logs_file = open(self.commandLogDir, 'w')
        json.dump(self.logs, logs_file)
        await self.console.print_console(level=2, number="1005", logText=f"Bot responds for guild {guildId} have been updated.")
        logs_file.close()

    async def initializeDoorLog(self, guildId):
        if self.bot.get_guild(id=int(guildId)):
            self.doorStatusNotificationChannelId = (self.logs["doorStatusNotificationChannels"])[str(guildId)]

    @tasks.loop(seconds=2)
    async def door_check(self):
        guild = self.bot.get_guild(id=699224778824745003)
        doorStatusNotificationChannel = discord.utils.get(guild.text_channels, id=int(self.doorStatusNotificationChannelId))
        trespassing, result = self.rpi.mech_door()
        if trespassing:
            member = result[0]
            await doorStatusNotificationChannel.send(f'**{member}** tarafından topluluk odası kapısı açıldı.')
            self.rpi.open_door()
        elif trespassing == False:
            cardid = result
            await doorStatusNotificationChannel.send(f'Kart numarası **{cardid}** olan birisi topluluk odası kapısını açmaya çalıştı.')

    @door_check.before_loop
    async def before_check(self):
        # waits until the bot is ready, then it starts the loop.
        await self.bot.wait_until_ready()
    
    @Cog.listener()
    async def on_message(self, ctx):
        guild = ctx.guild
        
        # * Filter conditions
        if ctx.author.bot:
            return
        if int(guild.id) in self.filterSettings.keys():
            if int(ctx.channel.id) in (self.filterSettings[int(guild.id)]).keys():
                if ((self.filterSettings[int(guild.id)])[int(ctx.channel.id)])['text'] and ctx.content != '':
                    try:
                        await ctx.delete()
                    except Exception as Err:
                        await self.console.print_console(level=4, number="1006", logText=f'{Err} raised at Commands/on_message.')
                        print(f'Errorx1006: {Err}')
                elif ((self.filterSettings[int(guild.id)])[int(ctx.channel.id)])['file'] and len(ctx.attachments):
                    try:
                        await ctx.delete()
                    except Exception as Err:
                        await self.console.print_console(level=4, number="1007", logText=f'{Err} raised at Commands/on_message.')
                        print(f'Errorx1007: {Err}')
        
        # * Bot responds
        data_general = self.botResponds["public"]
        if str(ctx.content).lower() in data_general.keys():
            await ctx.channel.send(f'**{data_general[str(ctx.content).lower()]}**')
            return
        elif str(ctx.content) in data_general.keys():
            await ctx.channel.send(f'**{data_general[str(ctx.content)]}**')
            return

        if int(guild.id) in self.botResponds.keys():
            data = self.botResponds[int(guild.id)]
            if str(ctx.content).lower() in data.keys():
                await ctx.channel.send(f'**{data[str(ctx.content).lower()]}**')
            elif str(ctx.content) in data.keys():
                await ctx.channel.send(f'**{data[str(ctx.content)]}**')

        elif int(guild.id) in self.botResponds2.keys():
            for cnt in (self.botResponds2)[int(guild.id)].keys():
                if cnt in str(ctx.content):
                    await ctx.channel.send(f'**{self.botrespond2[str(cnt)]}**')

                elif cnt in str(ctx.content).lower():
                    await ctx.channel.send(f'**{self.botrespond2[str(cnt)]}**')

        # * Mentioned in a message
        message = ctx
        if self.bot.user.mentioned_in(message):
            if message.channel.type != discord.ChannelType.private:
                await self.console.print_console(level=0, number="1009", logText=str(message.content))

    @command()
    @commands.has_permissions(manage_channels=True)
    async def listmembers(self, ctx):
        members = self.rpi.list_members()
        message_list = []
        member_list = [["Durum", "Pozisyon", "İsim", "Soyisim", "Kart Numarası"]]
        n = 0
        for member in members:
            if n == 10:
                message_list.append(member_list)
                member_list = [["Durum", "Pozisyon", "İsim", "Soyisim", "Kart Numarası"]]
                n = 0
            member_list.append([member["status"], member["position"], member["name"], member["surname"], member["cardid"]])
            n+=1
        message_list.append(member_list)
        tableObj = texttable.Texttable()
        for msg in message_list:
            # Set columns
            tableObj.set_cols_align(["c", "c", "c", "c", "c"])
            # Set datatype of each column
            tableObj.set_cols_dtype(["t", "t", "t", "t", "i"])
            # Adjust columns
            tableObj.set_cols_valign(["m", "m", "m", "m", "m"])
            # Insert rows
            tableObj.add_rows(msg)
            await ctx.send(f'```{tableObj.draw()}```')
            tableObj.reset()

    @command()
    @commands.has_permissions(manage_channels=True)
    async def addmember(self, ctx, status, position, name, surname, cardid):
        self.rpi.add_member(status, position, name, surname, cardid)
        await ctx.send("Kişi veri tabanına eklendi.")

    @command()
    @commands.has_permissions(manage_channels=True)
    async def removemember(self, ctx, name=None, surname=None):
        if surname == None:
            result = self.rpi.remove_member(name)
            if result == 1:
                await ctx.send("Kişi veri tabanından silindi.")
            elif result == 2:
                await ctx.send("Aynı kriterlere uygun birden fazla kişi bulunuyor.")
            else:
                await ctx.send("Kriterlere uygun kişi bulunamadı.")
        else:
            self.rpi.remove_member(name, surname)
            await ctx.send("Kişi veri tabanından silindi.")
                 
    @command()
    @commands.has_permissions(manage_channels=True)
    async def adduser(self, ctx, userId, channelId=None):
        guild = ctx.guild
        if channelId == None:
            channel = ctx.channel
        else:
            try:
                channel = discord.utils.get(guild.text_channels, id=int(channelId))
            except Exception as Err:
                await self.console.print_console(level=4, number="1008", logText=f'{Err} raised at Commands/adduser.')
                print(f'Errorx1008: {Err}')
                await ctx.send("The channel cannot be found!")
                return
        try:
            user = discord.utils.get(guild.members, id=int(userId))
        except:
            await ctx.send("The user cannot be found!")
            return
        try:
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = True
            overwrite.send_messages = True
            overwrite.read_messages = True
            overwrite.read_message_history = True
            await channel.set_permissions(user, overwrite=overwrite)
            await ctx.send(f'{user.name} is added to {channel.name}.')
        except Exception as Err:
            await self.console.print_console(level=4, number="1009", logText=f'{Err} raised at Commands/adduser.')
            print(f'Errorx1009: {Err}')
            await ctx.send("The user cannot be added!")

    @command()
    @commands.has_permissions(manage_channels=True)
    async def removeuser(self, ctx, userId, channelId=None):
        guild = ctx.guild
        if channelId == None:
            channel = ctx.channel
        else:
            try:
                channel = discord.utils.get(guild.text_channels, id=int(channelId))
            except Exception as Err:
                await self.console.print_console(level=4, number="1010", logText=f'{Err} raised at Commands/removeuser.')
                print(f'Errorx1010: {Err}')
                await ctx.send("The channel cannot be found!")
                return

        try:
            user = discord.utils.get(guild.members, id=int(userId))
        except:
            await ctx.send("The user cannot be found!")
            return
        if not user in channel.members:
            await ctx.send("The user is not in this channel.")
            return
        try:
            await channel.set_permissions(user, overwrite=None)
            await ctx.send(f'{user.name} is removed from {channel.name}.')
        except Exception as Err:
            #! await self.console.print_console(level=4, number="1011", logText=f'{Err} raised at Commands/removeuser.')
            print(f'Errorx1011: {Err}')
            await ctx.send("The user cannot be removed!")

    @command()
    @commands.has_permissions(manage_webhooks=True)
    async def clearwebhooks(self, ctx, channelId=None):
        try:
            channelWebhooks = await ctx.channel.webhooks()
            for w in channelWebhooks:
                await w.delete()
            await ctx.message.delete()
            await ctx.send("Kanalda bulunan webhooklar silindi.")
        except Exception as Err:
            await self.console.print_console(level=4, number="1012", logText=f'{Err} raised at Commands/clearwebhooks.')
            print(f'Errorx1012: {Err}')
            await ctx.send("İstek gerçekleştirilemedi!")

    @command()
    @commands.has_permissions(manage_channels=True)
    async def get(self, ctx, userId, channelId=None):
        guild = ctx.guild
        if not channelId:
            if ctx.author.voice:
                voiceChannel = ctx.author.voice.channel
            else:
                return
        else:
            try:
                voiceChannel = discord.utils.get(guild.text_channels, id=int(channelId))
            except Exception as Err:
                await self.console.print_console(level=4, number="1013", logText=f'{Err} raised at Commands/get.')
                print(f'Errorx1013: {Err}')
                await ctx.send("Couldn't get the user!")
                return
        try:
            targetUser = self.bot.get_user(userId)
        except Exception as Err:
            await self.console.print_console(level=4, number="1014", logText=f'{Err} raised at Commands/get.')
            print(f'Errorx1014: {Err}')
            return
        try:
            await targetUser.move_to(voiceChannel)
        except Exception as Err:
            await self.console.print_console(level=4, number="1015", logText=f'{Err} raised at Commands/get.')
            print(f'Errorx1015')

    @command()
    @commands.has_permissions(manage_channels=True)
    async def filter(self, ctx, on_off=None, filterType='text', channelId=None):
        guild = ctx.guild
        if not str(on_off).lower() in ['on', 'off']:
            return
        if not channelId:
            chnl = ctx.channel
        else:
            try:
                chnl = discord.utils.get(guild.text_channels, id=int(channelId))
            except Exception as Err:
                await ctx.send('İstek gerçekleştirilemedi, tekrar deneyin!')
                await self.console.print_console(level=4, number="1016", logText=f'{Err} raised at Commands/filter.')
                print(f'Errorx1016: {Err}')
                return
        
        on_off = True if str(on_off).lower() == 'on' else False
        otherFilterType = 'text' if str(filterType).lower() == 'file' else 'file'

        if int(guild.id) in self.filterSettings.keys():
            if int(chnl.id) in (self.filterSettings[int(guild.id)]).keys():
                ((self.filterSettings[int(guild.id)])[int(chnl.id)])[filterType] = on_off
            else:
                (self.filterSettings[int(guild.id)]).update({int(chnl.id):{str(filterType):on_off, str(otherFilterType):False}})
        else:
            self.filterSettings.update({int(guild.id):{int(chnl.id):{str(filterType):on_off, str(otherFilterType):False}}})
        await self.updateLog(int(guild.id), "filterSettings", value2=self.filterSettings[int(guild.id)])

    def arrange_time(self, text):
        text = str(text).split(' ')
        d = (text[0].split('-'))[::-1]
        t = (text[1].split(':'))
        t[-1] = str(round(float(t[-1])))
        d = f'{d[0]}.{d[1]}.{d[2]}'
        t = f'{t[0]}:{t[1]}:{t[1]}'
        return f'{t} {d}'
    
    @command()
    @commands.has_permissions(manage_messages=True)
    async def getlog(self, ctx, channelId=None):
        guild = ctx.guild
        if channelId == None:
            targetChannel = ctx.channel
        else:
            try:
                targetChannel = discord.utils.get(guild.text_channels, id=int(channelId))
            except Exception as Err:
                await self.console.print_console(level=4, number="1017", logText=f'{Err} raised at Commands/getlog.')
                print(f'Errorx1017: {Err}')
                await ctx.send('Kanal bulunamadı, tekrar deneyiniz!')
                return
        await ctx.message.delete()
        messages = await targetChannel.history(limit=None, oldest_first=True).flatten()

        log_content = f'###\tThis is the log file of the channel named {targetChannel.name} in {guild.name}.\n###\tThe log is taken by {ctx.author}.\n{time.strftime("###%tDate: %d.%m.%Y %n###%tTime: %H:%M:%S")} \n###\tThe first message time of the log is {self.arrange_time(messages[0].created_at)}.\n###\tThe last message time of the log is {self.arrange_time(messages[-1].created_at)}.\n\n'
        for msg in messages:
            msg_info = f'{msg.author} - {self.arrange_time(msg.created_at)} -- {msg.content}\n'
            log_content += msg_info
        print(log_content)

    @command(name='sad')
    async def sad(self, ctx):
        await ctx.message.delete()
        await ctx.send(":frowning:")
    
    @command()
    async def getcommands(self, ctx):
        for item in self.bot.commands:
            await ctx.send(item.name)

    @command()
    async def react(self, ctx, messageId, *, emoji):
        if int(ctx.author.id) == 565956579300737026:
            try:
                msg = await ctx.fetch_message(id=int(messageId))
                await ctx.message.delete()
                await msg.add_reaction(emoji)
            except:
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            msg = await channel.fetch_message(id=int(messageId))
                            await ctx.message.delete()
                            await msg.add_reaction(emoji)
                            return
                        except:
                            pass

    @command()
    async def unreact(self, ctx, messageId, *, emoji):
        guild = ctx.guild
        if int(ctx.author.id) == 565956579300737026:
            try:
                msg = await ctx.fetch_message(id=int(messageId))
                await ctx.message.delete()
                await msg.remove_reaction(emoji, guild.me)
            except:
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            msg = await channel.fetch_message(id=int(messageId))
                            await ctx.message.delete()
                            await msg.remove_reaction(emoji, guild.me)
                            return
                        except:
                            pass

    @command()
    async def message(self, ctx, *, msg):
        if int(ctx.author.id) == 565956579300737026:
            await ctx.message.delete()
            await ctx.send(msg)
    
    @command()
    async def msg(self, ctx, channelId, *, content):
        thisFile = 0
        if ctx.message.attachments:
            attch = ctx.message.attachments[0]
            thisFile = await attch.to_file()
        channel = self.bot.get_channel(int(channelId))
        if thisFile:
            await channel.send(content, file=thisFile)
        else:
            await channel.send(content)
        await ctx.message.delete()

    @command()
    async def msgedit(self, ctx, messageId, *, content):
        try:
            guild = ctx.guild
            for channel in guild.text_channels:
                try:
                    msg = await channel.fetch_message(int(messageId))
                    await msg.edit(content=content)
                    await ctx.message.delete()
                    return
                except:
                    pass
        except:
            pass

    @command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number):
        number = int(number) + 1
        counter = 0
        async for x in ctx.channel.history(limit = number):
            if counter < number:
                await x.delete()
                counter += 1
        if (counter-1) > 1:
            msg = f':white_check_mark: I have deleted {(counter-1)} messages.'
        elif (counter-1) == 1:
            msg = f':white_check_mark: I have deleted {(counter-1)} message.'
        else:
            msg = f':white_check_mark: I cannot delete any message.'
        bot_msg = await ctx.send(msg)
        time.sleep(1.2)
        await bot_msg.delete()

    @command(name='embed')
    @commands.has_permissions(manage_messages=True)
    async def embedMessage(self, ctx, *, text_msg):
        embed = Embed(description=text_msg, color=ctx.author.color)
        await ctx.send(embed=embed)
        await ctx.message.delete()
    


    @command()
    async def testConsole(self, ctx, level=2):
        await ctx.message.delete()
        if level < 5 and level > 0:
            pass
            #! await self.console.print_console(level=level)

    @command()
    async def testCmd(self, ctx):
        await ctx.message.delete()
        await ctx.send(self.doorStatusNotificationChannelId)
        #print(self.filterSettings)
        #print(self.botResponds)
        #print(self.commandServerLog)
        #await ctx.send(ctx.author.roles)
    
    @command()
    async def testCmd1(self, ctx, emj):
        guild = ctx.guild
        await ctx.message.add_reaction(str(emj))
        for emjj in guild.emojis:
            if emj == str(emjj):
                break
        await ctx.send(emjj.id)

    """
    @command(name='seslisil')
    @commands.has_permissions(manage_messages=True)
    async def seslisil(self, ctx):
        guild = ctx.guild
        for channel in guild.voice_channels:
            if "grup" in (str(channel.name)).lower():
                await channel.delete()
        await ctx.send("Sesli kanallar silindi.")
    
    @command(name='yazilisil')
    @commands.has_permissions(manage_messages=True)
    async def yazilisil(self, ctx):
        guild = ctx.guild
        for channel in guild.text_channels:
            if "grup" in (str(channel.name)).lower():
                await channel.delete()
        await ctx.send("Yazılı kanallar silindi.")
    """
