#the functions that create a channel with given members.
from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import Embed
import time, discord, random

class Group(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.randomgroups = {}
        self.createdgroups = {}

    @command(name="pdc_groups")
    @commands.has_permissions(manage_messages=True)
    async def pdc_groups(self, ctx):
        guild = ctx.guild
        observer1 = discord.utils.get(guild.roles, name='Arçelik')
        observer2 = discord.utils.get(guild.roles, name='Organizasyon Ekibi')
        category1 = discord.utils.get(guild.categories, name="EKİPLER")
        for n in range(21, 31):
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, view_channel=False),
                observer1: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True, read_message_history=True),
                observer2: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True, read_message_history=True)
                }
            
            if not discord.utils.get(guild.roles, name=f'grup{n}'):
                await guild.create_role(name=f'grup{n}')

            grup = discord.utils.get(guild.roles, name=f'grup{n}')
            overwrites.update({grup: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, read_message_history=True)})

            textchannel = await guild.create_text_channel(name=f'grup{n}', overwrites=overwrites, category=category1)
            voicechannel = await guild.create_voice_channel(name=f'grup{n}', overwrites=overwrites, category=category1)
    
    @command(name="listmembers")
    @commands.has_permissions(manage_messages=True)
    async def listmembers(self, ctx, *args):
        members = {}
        guild = ctx.guild
        error = False
        roles = list(a.name for a in guild.roles)
        n = 1
        if len(args) == 0:
            for member in guild.members:
                members.update({n:{"id":member.id, "nick":member.nick, "name":member.name}})
                n+=1
        elif len(args) == 1:
            if args[0] in roles:
                role = discord.utils.get(guild.roles, name=str(args[0]))
                for member in guild.members:
                    if role in member.roles:
                        members.update({n:{"id":member.id, "nick":member.nick, "name":member.name}})
                        n+=1
            else:
                await ctx.send("Rol bulunamadı!")
                error = True
        else:
            roleName = ' '.join(args)
            if roleName in roles:
                role = discord.utils.get(guild.roles, name=roleName)
                for member in guild.members:
                    if role in member.roles:
                        members.update({n:{"id":member.id, "nick":member.nick, "name":member.name}})
                        n+=1
            else:
                await ctx.send("Rol bulunamadı!")
                error = True
        if error == False:
            embeds = []
            if len(members.keys())%25 == 0:
                k = len(members.keys())/25
            else:
                k = int(len(members.keys())/25)+1
            for m in range(k):
                embeds.append(Embed(color=ctx.author.color))
            for n in members.keys():
                embeds[int(n/25)].add_field(name=n, value=f'Kullanıcı Adı: {(members[n])["nick"]}, Discord Adı: {(members[n])["name"]}, Kullanıcı Id: {(members[n])["id"]}', inline=False)
            for e in embeds:
                await ctx.send(embed=e)

    @command(name="randomgrup")
    @commands.has_permissions(manage_messages=True)
    async def randomgrup(self, ctx, capacity=5):
        guild = ctx.guild
        participants = {}
        groups = {}
        mekRole = discord.utils.get(guild.roles, name='Mekanizma')
        for member in guild.members:
            if mekRole in member.roles:
                participants.update({member.id:False})
        if len(participants) < 5:
            await ctx.send("Yeterli sayıda katılımcı yok.")
        elif len(participants)%5 == 0:
            n = len(participants)/5
        elif len(participants)%5 != 0:
            n = int(len(participants)/5)+1
        p = 0
        for k in range(n):
            group = []
            l = 0
            while l < capacity:
                willadd = random.choice(list(participants.keys()))
                if participants[willadd] == False:
                    group.append(willadd)
                    participants[willadd] = True
                    l+=1
                    p+=1
                elif p==len(participants):
                    break
            groups.update({f'grup{str(k+1)}':group})
        
        embeds = []
        l = len(groups.keys())
        if l%25 == 0:
            k = l/25
        else:
            k = int(l/25)+1
        for m in range(k):
            embeds.append(Embed(color=ctx.author.color))
        q = 0
        for group in groups.keys():
            field1 = ""
            for memberID in groups[group]:
                member = guild.get_member(memberID)
                field1 += f'**Kullanıcı adı:** {member.name} **Sunucudaki Adı:** {member.nick}\n'
            embeds[int(q/25)].add_field(name=group, value=field1, inline=False)
            q+=1
        for e in embeds:
            await ctx.send(embed=e)
        self.randomgroups = groups

    @command(name="randomgrupolustur")
    @commands.has_permissions(manage_messages=True)
    async def randomgrupolustur(self, ctx):
        guild = ctx.guild
        groups = self.randomgroups
        if self.createdgroups == {}:
            self.createdgroups.update({guild.id:{'voice':[], 'text':[]}})
        mentors = {}
        error = False
        try:
            mentor = discord.utils.get(guild.roles, name='Mentor')
            mothermentor = discord.utils.get(guild.roles, name='Ana Mentor')
        except:
            print("There is no mother mentor role.")
        for member in guild.members:
            if mentor in member.roles:
                mentors.update({member.id:0})

        if len(mentors) == 0:
            await ctx.send("Sunucuda mentor yok!")
            error = True
        
        c = 1
        n = 0
        for group in groups.keys():
            overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, view_channel=False),
                    mothermentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True, read_message_history=True)
                    }
            tf = False
            if error == True:
                break
            while not tf:
                randomMentorId = random.choice(list(mentors.keys()))
                if n < len(mentors.keys()):
                    if mentors[randomMentorId] < 1:
                        randomMentor = discord.utils.get(guild.members, id=randomMentorId)
                        overwrites.update({randomMentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True,  read_message_history=True)})
                        mentors[randomMentorId] += 1
                        tf = True
                        n+=1

                elif n < 2*len(mentors.keys()):
                    if mentors[randomMentorId] < 2:
                        randomMentor = discord.utils.get(guild.members, id=randomMentorId)
                        overwrites.update({randomMentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True,  read_message_history=True)})
                        mentors[randomMentorId] += 1
                        tf = True
                        n+=1
                
                else:
                    randomMentor = discord.utils.get(guild.members, id=randomMentorId)
                    overwrites.update({randomMentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True,  read_message_history=True)})
                    mentors[randomMentorId] += 1
                    tf = True
                    n+=1
            for memberId in groups[group]:
                member = discord.utils.get(guild.members, id=int(memberId))
                overwrites.update({member: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, read_message_history=True)})
            try:
                if int(c/25) == 0:
                    catName = 'Mekanizma'
                else:
                    catName = f'Mekanizma {int(c/25)+1}'
                try:
                    category = discord.utils.get(guild.categories, name=catName)
                except:
                    category = await guild.create_category(name=catName)
                textchannel = await guild.create_text_channel(name=group, overwrites=overwrites, category=category)
                (self.createdgroups[guild.id])["text"].append(textchannel.id)
                voicechannel = await guild.create_voice_channel(name=group, overwrites=overwrites, category=category)
                (self.createdgroups[guild.id])["voice"].append(voicechannel.id)
                c+=1
            except:
                print("The channels cannot be created!")

    @command(name="grup")
    @commands.has_permissions(manage_messages=True)
    async def group(self, ctx, *given):
        guild = ctx.guild
        members = given
        mentor = ""
        error = False
        made = False
        try:
            mothermentor = discord.utils.get(guild.roles, name=self.mothermentorname)
        except:
            print("There is no mother mentor role.")

        if str(members[0]).lower() == "mentor:":
            memberIDs = []
            try:
                mentorID = str(members[1]).split("!")
                mentorID = int((mentorID[1].split(">"))[0])
                mentor = discord.utils.get(guild.members, id=mentorID)
            except:
                print("The mentor cannot be found!")
                error = True

            if str(members[2]).lower() == "eklenecekler:":
                for item in list(members[3:]):
                    if item == "isim:":
                        break
                    try:
                        memberID = str(item).split("!")
                        memberID = int((memberID[1].split(">"))[0])
                        memberIDs.append(memberID)
                    except:
                        print("The member id is wrong!")
                        error = True
            try:
                if str(members[-2]) == "isim:":
                    channelname = str(members[-1])
            except:
                print("The channel's name cannot found.")
                error = True
        
        else:
            memberIDs = []
            try:
                for item in list(members):
                    if item == "isim:":
                        break
                    try:
                        memberID = str(item).split("!")
                        memberID = int((memberID[1].split(">"))[0])
                        memberIDs.append(memberID)
                    except:
                        print("The member id is wrong!")
                        error = True
            except:
                print("The users cannot be found!")
                error = True

            if str(members[-2]) == "isim:":
                channelname = str(members[-1])
            else:
                print("The channel's name cannot found.")
                error = True

        if error == False:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, view_channel=False)
                }
                participants = []
                overwrites.update({mothermentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True, read_message_history=True)})
                if not mentor == "" or mothermentor == None:
                    overwrites.update({mentor: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, manage_messages=True,  read_message_history=True)})
                    
                    participants.append(mentor.nick)
                else:
                    print("There is no mentor.")
                
                for ID in memberIDs:
                    try:
                        member = discord.utils.get(guild.members, id=ID)
                        participants.append(member.nick)
                        overwrites.update({member: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, connect=True, speak=True, stream=True, read_message_history=True)})
                    except:
                        print("The user cannot be found!")
                try:
                    category = discord.utils.get(guild.categories, name="Mentorlu Projeler2")
                    textchannel = await guild.create_text_channel(name=channelname, overwrites=overwrites, category=category)
                    voicechannel = await guild.create_voice_channel(name=channelname, overwrites=overwrites, category=category)
                    made = True
                except:
                    print("The channels cannot be created!")
            except:
                print("ERROR")
        
        if made == True:
            with open(f'Logs.{str(guild.id)}.groups.txt', 'a') as groups:
                try:
                    groups.write(f'Text Channel: {textchannel.name}; Voice Channel: {voicechannel.name}; participants: {participants}\n')
                except:
                    print("The group cannot be written to text.")
    
    @command(name='listgroups')
    @commands.has_permissions(manage_messages=True)
    async def listgroups(self, ctx):
        guild = ctx.guild
        embed = Embed(title='Gruplar', description='Bot tarafından oluşturulan gruplar: ')
        with open(f'Logs.{str(guild.id)}.groups.txt', 'r') as groups:
            n = 1
            for line in groups:
                line = line.split("; ")
                text = f'Yazılı Kanal: {(line[0].split(": "))[1]} \nSesli Kanal: {(line[1].split(": "))[1]} \nKişiler: {(line[2].split(": "))[1]}'
                embed.add_field(name=f'{n}- Kanal: {(line[0].split(": "))[1]}', value=f'{text}', inline=False)
                n+=1
        await ctx.send(embed=embed)

    @command(name='deletegroup')
    @commands.has_permissions(manage_messages=True)
    async def delgroup(self, ctx, group):
        guild = ctx.guild
        if group == "all":
            with open(f'Logs.{str(guild.id)}.groups.txt', 'r') as groups:
                for line in groups:   
                    line = line.split("; ")
                    textchannel = discord.utils.get(guild.text_channels, name=(line[0].split(": "))[1])
                    voicechannel = discord.utils.get(guild.voice_channels, name=(line[1].split(": "))[1])
                    await textchannel.delete()
                    await voicechannel.delete()
            with open(f'Logs.{str(guild.id)}.groups.txt', 'a') as clean:
                clean.truncate(0)
                print("All channels have been deleted.")
                await ctx.send("Sunucudaki Mecha tarafından oluşturulan tüm kanallar silindi.")
                
        else:
            try:
                deleted = False
                with open(f'Logs.{str(guild.id)}.groups.txt', 'r') as groups:
                    n = 1
                    for line in groups:
                        if n == int(group):
                            line = line.split("; ")
                            textchannel = discord.utils.get(guild.text_channels, name=(line[0].split(": "))[1])
                            voicechannel = discord.utils.get(guild.voice_channels, name=(line[1].split(": "))[1])
                            await textchannel.delete()
                            await voicechannel.delete()
                            deleted = True
                            break
                        n+=1

                groups = open(f'Logs.{str(guild.id)}.groups.txt', 'r')
                if deleted == True:
                    contents = groups.readlines()
                    contents.pop(n-1)
                groups.close()
                
                if deleted == True:
                    with open(f'Logs.{str(guild.id)}.groups.txt', 'w') as groups:
                        contents = "".join(contents)
                        groups.write(contents)
                    print("The channel is deleted.")
                    await ctx.send(f'{textchannel.name} isimli yazılı kanal ve {voicechannel.name} isimli sesli kanal silindi.')

            except:
                print("The channels cannot be deleted or not exist.")
