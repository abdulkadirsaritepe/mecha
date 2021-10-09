import re
import discord, aiohttp, asyncio, time
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command
from discord import Embed
import requests, datetime, random, json, sys

class Youtube(Cog):
    def __init__(self, bot, console):
        self.bot = bot
        self.console = console
        if sys.platform == "linux":
            rpi_os = True
            self.logDir = "/home/pi/asbot/mekanik/cogs/Logs" #! 
            self.accountsLogDir = f'{self.logDir}/socialmedia.json'
        else:
            rpi_os = False
            self.logDir = "C:\Dev\Github\src\mekanik\cogs\Logs"
            self.accountsLogDir = f'{self.logDir}\socialmedia.json'
        # dictionary variable to store youtube channels informations for checking.
        self.accounts = {}
        
    @Cog.listener()
    async def on_ready(self):
        # when the bot is ready, it is started.
        with open(self.accountsLogDir) as accountsLogFile:
            self.accounts = (json.load(accountsLogFile))["youtube"]
        await self.console.print_console(level=2, number='7000', logText='Youtube Channels List has been updated.')
        self.videoCheck.start()
        await self.console.print_console(level=2, number='7001', logText='Youtube video check task has been started.')

    async def youtube(self, url):
        videos = []
        # take source code of youtube channel website
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                req = await response.text()
        # arrange the taken data
        ytData = (str(req[req.find('{"itemSectionRenderer":{"contents":[{"gridRenderer":{"items":[')+len('{"itemSectionRenderer":{"contents":[{"gridRenderer":{"items":['):req.find(',{"continuationItemRenderer"')]))
        # change true and false with True and False since python uses capital letter
        ytData = ytData.replace('true', 'True')
        ytData = ytData.replace('false', 'False')
        # convert string data to list of videos data
        ytData = eval(ytData)
        # arrange n according to ytdata length
        # if length is greater than 5, n = 5
        n = len(ytData) if len(ytData) < 5 else 5
        # take last 5 or less video id
        for k in range(n):
            videoData = ytData[k]
            videoData = videoData['gridVideoRenderer']
            videoId = videoData['videoId']
            if len(videoId) < 20:
                videos.append(videoId)
            else:
                # if the id data is broken return null list
                return []
        return videos

    @tasks.loop(seconds=60.0)
    async def videoCheck(self):
        # the loop function for checking the given youtube channels latest videos
        for ytch in self.accounts.keys():
            # if video check is enabled and videosurl is not empty, it runs.
            if (self.accounts[ytch])["active"] == True and (self.accounts[ytch])["videosurl"] != "":
                # try to get the latest videos 
                try:
                    # get channel's url and take the information
                    yturl = (self.accounts[ytch])["videosurl"]
                    ytcheck = await self.youtube(yturl)
                    # if the latest video is not in the lastpost array, then perform upcoming operations.
                    if not ytcheck[0] in (self.accounts[ytch])["lastpost"]:
                        # if lastpost array is empty, just update it.
                        if (self.accounts[ytch])["lastpost"] != []:
                            # if not send notification to the given channels
                            for guildId in (self.accounts[ytch])["server"].keys():
                                # try to get notification channel and send the information message
                                try:
                                    guild = discord.utils.get(self.bot.guilds, id=int(guildId))
                                    notification_channel = self.bot.get_channel(int(((self.accounts[ytch])["server"])[guildId]))
                                    await notification_channel.send(f'**Yeni video yayında!** @everyone https://www.youtube.com/watch?v={ytcheck[0]}')
                                # if some error occurs, print it.
                                except Exception as err:
                                    await self.console.print_console(level=4, number='7011', logText=f'Youtube - {err} at {guild.name} - {ytch} - videocheck')
                                    print(f'Errorx7011: youtube {err} at {guild.name} while sending- {ytch}')
                        (self.accounts[ytch])["lastpost"] = ytcheck
                
                # if some error occurs, it prints the error type.
                except Exception as err:
                    await self.console.print_console(level=4, number='7012', logText=f'Youtube - {err} at {guild.name} - {ytch} - videocheck')
                    print(f'Errorx7012: youtube {err} while checking- {ytch}') 

    @videoCheck.before_loop
    async def before_check(self):
        # waits until the bot is ready, then it starts the loop.
        await self.bot.wait_until_ready()

    @command(name='youtubeinfo')
    @commands.has_permissions(manage_messages=True)
    async def youtubeinfo(self, ctx):
        # when youtubeinfo command typed, the bot sends the youtube informations for that guild.
        guild = ctx.guild
        youtube_channels = {}
        try:
            log = "```diff\n- YOUTUBE: \n"
            for ytch in (self.accounts.keys()):
                if str(guild.id) in ((self.accounts[ytch])['server']).keys():
                    youtube_channels.update({ytch:{'channel':((self.accounts[ytch])['server'])[str(guild.id)], 'videosurl':(self.accounts[ytch])['videosurl'], 'lastposts':(self.accounts[ytch])['lastpost']}})
                    if (self.accounts[ytch])['active'] == False:
                        youtube_channels[ytch].update({'lastposts':"False"})
            
            for l in youtube_channels.keys():
                log+=f'+ {l.upper()}\n'
                for k in youtube_channels[l]:
                    log+=f'\t{k.upper()} = {(youtube_channels[l])[k]}\n'
            log+="```"
            await ctx.send(log)
        except Exception as Err:
            await self.console.print_console(level=4, number='7021', logText=f'Youtube - {Err} at {guild.name} - youtubeinfo')
            print(f'Errorx7021: {Err}')
            print(f'There is no info about the guild {guild.name}.')

    @command()
    @commands.has_permissions(manage_messages=True)
    async def addytchannel(self, ctx, ytChannelUrl=None, dcChannelId=None):
        guild = ctx.guild
        try:
            await self.youtube(ytChannelUrl)
        except:
            await ctx.send('Kanal linki kontrol edilirken hata oluştu.')
            return
        try:
            notificationChannel = discord.utils.get(guild.text_channels, id=int(dcChannelId))
        except:
            await ctx.send('Bildirim kanalı bulunamadı.')
            return
        ytChannelName = (str(ytChannelUrl).split("www.youtube.com/c/"))[1]
        ytChannelName = ((ytChannelName.split("/videos"))[0]).lower()
        with open(self.accountsLogDir) as accountsLogFile:
            data = json.load(accountsLogFile)
        if ytChannelName in (data["youtube"]).keys():
            (((data["youtube"])[ytChannelName])["server"]).update({str(guild.id):int(dcChannelId)})
            await ctx.send(f'Girilen youtube kanalı -{ytChannelName}- sunucunun listesine eklendi.')
        else:
            (data["youtube"]).update({ytChannelName:{"active":True, "videosurl":str(ytChannelUrl), "lastpost":[], "server":{str(guild.id):int(dcChannelId)}}})
            await ctx.send(f'Girilen youtube kanalı -{ytChannelName}- sunucunun listesine eklendi.')
        with open(self.accountsLogDir, "w") as accountsLogFile:
            json.dump(data, accountsLogFile)
        self.accounts = data["youtube"]
        await self.videoCheck()

    @command()
    @commands.has_permissions(manage_messages=True)
    async def removeytchannel(self, ctx, ytChannelName=None):
        guild = ctx.guild
        ytChannelName = str(ytChannelName).lower()
        with open(self.accountsLogDir) as accountsLogFile:
            data = json.load(accountsLogFile)
        if ytChannelName in (data["youtube"]).keys():
            if str(guild.id) in (((data["youtube"])[ytChannelName])["server"]).keys():
                (((data["youtube"])[ytChannelName])["server"]).pop(str(guild.id), None)
                await ctx.send(f'Girilen youtube kanalı -{ytChannelName}- sunucunun listesinden çıkarıldı.')
            else:
                await ctx.send(f'Girilen youtube kanalı -{ytChannelName}- sunucu listesinde bu sunucu zaten bulunmamaktadır.')
        else:
            await ctx.send(f'Girilen youtube kanalı -{ytChannelName}- listede bulunmamaktadır.')
        with open(self.accountsLogDir, "w") as accountsLogFile:
            json.dump(data, accountsLogFile)
        self.accounts = data["youtube"]
        await self.videoCheck()

class Instagram(Cog):
    def __init__(self, bot, console):
        self.bot = bot
        if sys.platform == "linux":
            rpi_os = True
            self.logDir = "/home/pi/asbot/mekanik/cogs/Logs" #! 
            self.accountsLogDir = f'{self.logDir}/socialmedia.json'
        else:
            rpi_os = False
            self.logDir = "C:\Dev\Github\src\mekanik\cogs\Logs"
            self.accountsLogDir = f'{self.logDir}\socialmedia.json'
        self.console = console
        # dictionary variable to store instagram accounts' informations for checking.
        self.accounts = {}
        self.allcolors = [0, 0x1abc9c, 0x11806a, 0x2ecc71, 0x1f8b4c, 0x3498db, 0x206694, 0x9b59b6, 0x71368a, 0xe91e63, 0xad1457, 0xf1c40f, 0xc27c0e, 0xe67e22, 0xa84300, 0xe74c3c, 0x992d22, 0x95a5a6, 0x607d8b, 0x979c9f, 0x546e7a, 0x7289da, 0x99aab5]
        self.colors = [0x1abc9c, 0x11806a, 0x3498db, 0x206694, 0x7289da, 0xc27c0e, 0xf1c40f]
        self.session = None
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/59.0.3071.115 Safari/537.36'
        self.login_info = []
    
    @Cog.listener()
    async def on_ready(self):
        with open(self.accountsLogDir) as accountsLogFile:
            self.accounts = (json.load(accountsLogFile))["instagram"]
        await self.console.print_console(level=2, number='8000', logText='Instagram Accounts List has been updated.')
        self.postCheck.start()
        await self.console.print_console(level=2, number='8001', logText='Instagram post check task has been started.')
    
    async def get_login_info(self):
        with open(f'{self.logDir}\\admin.json') as loginInfoFile:
            data = json.load(loginInfoFile)
            self.login_info = [(data["instagram_login_info"])["username"], (data["instagram_login_info"])["password"]]
        await self.console.print_console(level=2, number='8002', logText='Instagram Login Information has been taken.')

    async def login(self, username, password):
        """Login to Instagram"""

        time = str(int(datetime.datetime.now().timestamp()))
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{password}"

        session = requests.Session()
        # set a cookie that signals Instagram the "Accept cookie" banner was closed
        session.cookies.set("ig_cb", "2")
        session.headers.update({'user-agent': self.user_agent})
        session.headers.update({'Referer': 'https://www.instagram.com'})
        res = session.get('https://www.instagram.com')

        csrftoken = None

        for key in res.cookies.keys():
            if key == 'csrftoken':
                csrftoken = session.cookies['csrftoken']

        session.headers.update({'X-CSRFToken': csrftoken})
        login_data = {'username': username, 'enc_password': enc_password}

        login = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
        session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})

        cookies = login.cookies
        print("Login is succcessfull!")
        await self.console.print_console(level=2, number='8011', logText='Login is succcessfull!')
        print("Login Information: " + login.text)
        await self.console.print_console(level=2, number='8012', logText=f'Login Information: {login.text}')
        self.session = session
    
    async def instagram_check(self, url):
        response2 = self.session.get(url)
        req2 = response2.text         
        try:
            profilePic = str(req2[req2.find(',"profile_pic_url":"')+len(',"profile_pic_url":"'):req2.find('","profile_pic_url_hd":')])
        except:
            profilePic = None
        postList = (req2.split("__typename"))[1:]
        igTF, postTF = False, False
        igtv, postStr = None, None
        for post in postList:
            if 'igtv' in post:
                if igTF == False:
                    igtv = post
                    igTF = True
            elif postTF == False:
                postStr = post
                postTF = True
            else:
                break
        if postStr != None:
            feed = str(postStr[postStr.find('"shortcode":"')+len('"shortcode":"'):postStr.find('","dimensions"')])
        else:
            feed = None
        if igtv != None:
            igtv = str(igtv[igtv.find('"shortcode":"')+len('"shortcode":"'):igtv.find('","dimensions"')])
        else:
            igtv = None
        if feed != None:
            posturl = f'https://www.instagram.com/p/{feed}?__a=1'

            response3 = self.session.get(posturl)
            req3 = response3.text 
            try:
                post = str(req3[req3.find(',"display_url":"')+len(',"display_url":"'):req3.find('","display_resources":')])  
            except:
                post = None
        else:
            post = None

        if igtv != None:
            igtvurl = f'https://www.instagram.com/p/{igtv}?__a=1'
            
            response4 = self.session.get(igtvurl)
            req4 = response4.text 
            try:
                igpost = str(req4[req4.find(',"display_url":"')+len(',"display_url":"'):req4.find('","display_resources":')])  
            except:
                igpost = None
        else:
            igpost = None

        return feed, igtv, profilePic, post, igpost
    
    @tasks.loop(seconds=60.0)
    async def postCheck(self):
        timer = 0
        while self.session == None:
            print("Logout From Instagram!")
            await self.console.print_console(level=3, number='8020', logText='Logout From Instagram!')
            try:
                print("Trying to login...")
                await self.console.print_console(level=2, number='8021', logText='Trying to login...')
                await self.get_login_info()
                if len(self.login_info) != 0:
                    await self.login(self.login_info[0], self.login_info[1])
            except:
                timer += 1
            if timer > 5:
                print("Couldn't connected to the account!")
                await self.console.print_console(level=4, number='8022', logText="Couldn't connected to the account!")
                self.postCheck.stop()
                return
        for instach in self.accounts.keys():
            if (self.accounts[instach])["active"] and (self.accounts[instach])["username"] != "":
                try:
                    username = str((self.accounts[instach])["username"])
                    instaurl = f'https://www.instagram.com/{username}/?__a=1'
                    feed, igtv, profilePic, post, igpost = await self.instagram_check(instaurl)
                    if feed != None:
                        if (self.accounts[instach])["lastpost"] != feed and len(feed) < 20:
                            if (self.accounts[instach])["lastpost"] != "":   
                                color = random.choice(self.colors)
                                embed = Embed(color=color)
                                embed.add_field(name=username, value=f'https://www.instagram.com/p/{feed}/')
                                if profilePic != None:
                                    try:
                                        embed.set_thumbnail(url=profilePic)
                                    except Exception as Err:
                                        print(f"Errorx8023: {Err}")
                                        await self.console.print_console(level=4, number='8023', logText="Instagram - {Err} at instagramcheck while creating embed.")
                                if post != None:
                                    try:
                                        embed.set_image(url=post)
                                    except Exception as Err:
                                        print(f"Errorx80244: {Err}")
                                        await self.console.print_console(level=4, number='8024', logText="Instagram - {Err} at instagramcheck while creating embed.")
                                for guild in self.bot.guilds:
                                    try:
                                        mediachannel = self.bot.get_channel(int(((self.accounts[instach])["server"])[str(guild.id)]))
                                        await mediachannel.send(content=f'**{username}** yeni gönderi paylaştı! @everyone',
                                                                embed=embed)
                                    except Exception as err:
                                        print(f'Errorx8025: instagram at {guild.name} - {(self.accounts[instach])["username"]} - Error: {err}')
                                        await self.console.print_console(level=4, number='8025', logText=f'Instagram - {err} at {guild.name} - {(self.accounts[instach])["username"]}')
                            (self.accounts[instach])["lastpost"] = feed
                    if igtv != None:
                        if (self.accounts[instach])["igtv"] != igtv and len(igtv) < 20:
                            if (self.accounts[instach])["igtv"] != "":
                                color = random.choice(self.colors)
                                embed2 = Embed(color=color)
                                embed2.add_field(name=username, value=f'https://www.instagram.com/p/{igtv}/')
                                if profilePic != None:
                                    try:
                                        embed2.set_thumbnail(url=profilePic)
                                    except Exception as Err:
                                        print(f"Errorx8026: {Err}")
                                        await self.console.print_console(level=4, number='8026', logText="Instagram - {Err} at instagramcheck while creating embed.")
                                    
                                if igpost != None:
                                    try:
                                        embed2.set_image(url=igpost)
                                    except Exception as Err:
                                        print(f"Errorx8027: {Err}")
                                        await self.console.print_console(level=4, number='8027', logText="Instagram - {Err} at instagramcheck while creating embed.")
                                for guild in self.bot.guilds:
                                    try:
                                        mediachannel = self.bot.get_channel(int(((self.accounts[instach])["server"])[str(guild.id)]))
                                        await mediachannel.send(content=f'**{username}** yeni gönderi paylaştı! @everyone',
                                                                embed=embed2)
                                    except Exception as err:
                                        print(f'Errorx8028: instagram at {guild.name} - {(self.accounts[instach])["username"]} - Error: {err}')
                                        await self.console.print_console(level=4, number='8028', logText=f'Instagram - {err} at {guild.name} - {(self.accounts[instach])["username"]}')
                            (self.accounts[instach])["igtv"] = igtv
                except Exception as err:
                    print(f'Errorx8029: instagram - {(self.accounts[instach])["username"]} - Error: {err}')
                    await self.console.print_console(level=4, number='8029', logText=f'{err} at {guild.name} - {(self.accounts[instach])["username"]}')
                     
    @postCheck.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()
        print("Trying to login instagram...")
        await self.console.print_console(level=2, number='8030', logText='Trying to login...')
        while self.session == None:
            try:
                await self.get_login_info()
                if len(self.login_info) != 0:
                    await self.login(self.login_info[0], self.login_info[1])
            except Exception as Err:
                print(f'Mekanik could not connect instagram. Errorx8031: {Err}')
                await self.console.print_console(level=4, number='8031', logText=f'Instagram - {Err} - Mekanik could not connect instagram.')

    @command()
    async def insta(self, ctx, url):
        msg = ctx.message
        text_url = f'{url}?__a=1'
        response = self.session.get(text_url)
        req = response.text
        try:
            post = str(req[req.find(',"display_url":"')+len(',"display_url":"'):req.find('","display_resources":')])
        except:
            post = None
        if post != None and len(post) < 1000:
            embed = Embed(color=random.choice(self.allcolors))
            embed.add_field(name='Picture', value=url)
            embed.set_image(url=post)
            await ctx.send(embed=embed)
            await msg.delete()
        else:
            await ctx.send("The post could not be found.")

    @command(name='instagraminfo')
    @commands.has_permissions(manage_messages=True)
    async def instagraminfo(self, ctx):
        guild = ctx.guild
        instaAcc = {}
        for acc in self.accounts.keys():
            if str(guild.id) in ((self.accounts[acc])["server"]).keys():
                if (self.accounts[acc])["active"] == True:
                    instaAcc.update({acc:{'username':(self.accounts[acc])["username"], 'lastpost':(self.accounts[acc])["lastpost"], 'igtv':(self.accounts[acc])["igtv"]}})
                else:
                    instaAcc.update({acc:{'username':'', 'lastpost':'', 'igtv':''}})
        try:
            log = "```diff\n- INSTAGRAM: \n"
            for acc in instaAcc.keys():
                log+=f'+ {acc.upper()}\n'
                for k in instaAcc[acc]:
                    log+=f'\t{k.upper()} = {(instaAcc[acc])[k]}\n'
            log+="```"
            await ctx.send(log)
        except Exception as Err:
            await self.console.print_console(level=4, number='8041', logText=f'Instagram - {Err} at {guild.name} - instagraminfo')
            print(f'Errorx8041: {Err}')
            print(f'There is no info about the guild {guild.name}.')

    @command()
    @commands.has_permissions(manage_messages=True)
    async def addinstagramaccount(self, ctx, username=None, dcChannelId=None):
        guild = ctx.guild
        try:
            instaurl = f'https://www.instagram.com/{username}/?__a=1'
            await self.instagram_check(instaurl)
        except:
            await ctx.send('Hesap kontrol edilirken hata oluştu.')
            return
        try:
            notificationChannel = discord.utils.get(guild.text_channels, id=int(dcChannelId))
        except:
            await ctx.send('Bildirim kanalı bulunamadı.')
            return
        with open(self.accountsLogDir) as accountsLogFile:
            data = json.load(accountsLogFile)
        if username in (data["instagram"]).keys():
            (((data["instagram"])[username])["server"]).update({str(guild.id):int(dcChannelId)})
            await ctx.send(f'Girilen instagram hesabı -{username}- sunucunun listesine eklendi.')
        else:
            (data["instagram"]).update({username:{"active":True, "username":str(username), "lastpost":"", "igtv":"", "server": {str(guild.id):int(dcChannelId)}}})
            await ctx.send(f'Girilen instagram hesabı -{username}- sunucunun listesine eklendi.')
        with open(self.accountsLogDir, "w") as accountsLogFile:
            json.dump(data, accountsLogFile)
        self.accounts = data["instagram"]
        await self.postCheck()

    @command()
    @commands.has_permissions(manage_messages=True)
    async def removeinstagramaccount(self, ctx, username=None):
        guild = ctx.guild
        username = str(username).lower()
        with open(self.accountsLogDir) as accountsLogFile:
            data = json.load(accountsLogFile)
        if username in (data["instagram"]).keys():
            if str(guild.id) in (((data["instagram"])[username])["server"]).keys():
                (((data["instagram"])[username])["server"]).pop(str(guild.id), None)
                await ctx.send(f'Girilen instagram hesabı -{username}- sunucunun listesinden çıkarıldı.')
            else:
                await ctx.send(f'Girilen instagram hesabı -{username}- sunucu listesinde bu sunucu zaten bulunmamaktadır.')
        else:
            await ctx.send(f'Girilen instagram hesabı -{username}- listede bulunmamaktadır.')
        with open(self.accountsLogDir, "w") as accountsLogFile:
            json.dump(data, accountsLogFile)
        self.accounts = data["instagram"]
        await self.postCheck()

    async def close(self):
        self.session.close()
        await self.console.print_console(level=2, number='8099', logText='Instagram Class has been closed.')

