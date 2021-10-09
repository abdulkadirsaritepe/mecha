from discord.ext.commands import Cog, command
import datetime
from discord import Embed, File
import aiohttp
from discord import Webhook, AsyncWebhookAdapter
from urllib.request import Request, urlopen


class ReactionCheck(Cog):
    def __init__(self, bot):
        self.bot = bot



    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == "❔":
            author_roles = (a.name for a in payload.member.roles)
            #
            if "Yönetim Kurulu" in author_roles:
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction("❔", payload.member)
                reactions = message.reactions
                reacted_users = []
                for a in reactions:
                    r_users = await a.users().flatten()
                    for k in r_users:
                        if k not in reacted_users:
                            reacted_users.append(k)

                all_users = message.channel.members
                

                index = 0
                for a in range(len(all_users)):

                    if all_users[index].bot:

                        del all_users[index]
                        continue
                    elif all_users[index] in reacted_users:

                        del all_users[index]
                        continue
                    index += 1
                    
                all_users_names = [None] * len(all_users)
                
                for i, a in enumerate(all_users):
                    all_users_names[i] = a.display_name
                    all_users[i] = a.mention

                if payload.member.dm_channel == None:
                    await payload.member.create_dm()
                usr_dm = payload.member.dm_channel
                message_time = message.created_at
                message_time += datetime.timedelta(hours=3)
                message_time = message_time.strftime("%H:%M:%S %d/%m/%Y")
                await usr_dm.send("{} tarafından gönderilen, {} kanalındaki {} tarihli\n\n{}\nmesajına tepki eklemeyen kişiler: {}".format(message.author.display_name,message.channel.mention,message_time,"```{}```".format(message.content),', '.join(all_users_names)))
                await usr_dm.send("```{}```".format(' '.join(all_users)))
