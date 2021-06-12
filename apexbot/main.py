import discord # type: ignore
import os
import sys
from typing import cast, Optional


try:
    TOKEN = os.environ['DISCORD_TOKEN']
except KeyError:
    print('Please set DISCORD_TOKEN')
    sys.exit(1)
if not TOKEN:
    print('Please set DISCORD_TOKEN')
    sys.exit(1)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

def _find_channel(guild: discord.Guild, chan_name: str) -> Optional[discord.TextChannel]:
    last_text_channel = None
    for chan in guild.channels:
        if not isinstance(chan, discord.TextChannel):
            continue
        if chan.name == chan_name:
            return chan
        last_text_channel = chan
    print(f'could not find #{chan_name} in {guild.name}')
    return last_text_channel

async def _send_member_online_notification(member: discord.Member) -> None:
    guild = member.guild
    chan = _find_channel(guild, 'online-status')
    if not chan:
        return
    content = f'{member.display_name} がオンラインになりました'
    await chan.send(content=content)

async def _send_start_game_notification(member: discord.Member) -> None:
    guild = member.guild
    playing = cast(discord.Game, member.activity).name
    chan = _find_channel(guild, 'online-status')
    if chan:
        content = f'${member.display_name} が ${playing} を始めました'
        await chan.send(content=content)

@client.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    print(f'member update ${str(before)} ${after}')
    if isinstance(after.status, str):
        return
    if after.status == discord.Status.online \
       and before.status != discord.Status.online:
        await _send_member_online_notification(after)
    elif isinstance(after.activity, discord.Game):
        after_game = after.activity.name
        if isinstance(before.activity, discord.Game):
            before_game = before.activity.name
            if after_game != before_game:
                await _send_start_game_notification(after)
        else:
            await _send_start_game_notification(after)


client.run(TOKEN)
