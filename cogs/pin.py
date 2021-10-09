from discord.ext.commands import Cog, command
from discord import Embed, File
from discord.ext import commands
import os, discord

class Pin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "📌"

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == self.emoji:
            channel = self.bot.get_channel(payload.channel_id)
            if int(payload.guild_id) == 699224778824745003:
                member_roles = list(a.name for a in payload.member.roles)
                if 'sabitleyici' in member_roles:
                    message = await channel.fetch_message(payload.message_id)
                    if not message.pinned:
                        await message.pin()
                        async for x in channel.history(limit = 1):
                            await x.delete()
            else:
                pers = list(a for a in channel.permissions_for(payload.member))
                if pers[13][1] == True:
                    message = await channel.fetch_message(payload.message_id)
                    if not message.pinned:
                        await message.pin()
                        async for x in channel.history(limit = 1):
                            await x.delete()

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name == self.emoji:
            channel = self.bot.get_channel(payload.channel_id)
            member = discord.utils.get(self.bot.get_all_members(), id=payload.user_id)
            if int(payload.guild_id) == 699224778824745003:
                member_roles = list(a.name for a in member.roles)
                print(member_roles)
                if 'sabitleyici' in member_roles:
                    message = await channel.fetch_message(payload.message_id)
                    if message.pinned:
                        await message.unpin()
            else:
                pers = list(a for a in channel.permissions_for(member))
                if pers[13][1] == True:
                    message = await channel.fetch_message(payload.message_id)
                    if message.pinned:
                        await message.unpin()

