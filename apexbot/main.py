import discord # type: ignore
import os
import sys
from typing import cast, Optional, Tuple, Union
import logging

logging.basicConfig(level=logging.INFO)

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
    for chan in guild.channels:
        if not isinstance(chan, discord.TextChannel):
            continue
        if chan.name == chan_name:
            return chan
    logging.info(f'could not find #{chan_name} in {guild.name}')
    return None

NOTIFYCHAN = 'apexability-check'

async def _send_apex_notification(member: discord.Member, game: str, is_start: bool) -> None:
    guild = member.guild
    chan = _find_channel(guild, NOTIFYCHAN)
    if chan:
        if is_start:
            tail = 'を始めました！'
        else:
            tail = 'をやめました！'
        content = f'{member.display_name} が {game} {tail}'
        await chan.send(content=content)

ActType = Union[discord.BaseActivity, discord.Spotify]
APEXGAME = "Apex Legends"
CUSTOM_APEXGAME = "AL"

def apex_started(oldActs: Tuple[ActType], newActs: Tuple[ActType]) -> bool:
    # APEX はプレイしていなかったことを確認
    for act in oldActs:
        if (isinstance(act, discord.Spotify)):
            continue
        if act.type == discord.ActivityType.playing and act.name == APEXGAME:
            # playing Apex Legends
            return False
        elif act.type == discord.ActivityType.custom and act.name == CUSTOM_APEXGAME:
            # custom "AL"
            return False
    
    # 今 APEX をプレイしていることを確認
    for act in newActs:
        if (isinstance(act, discord.Spotify)):
            continue
        if act.type == discord.ActivityType.playing and act.name == APEXGAME:
            return True
    return False

def apex_stopped(oldActs: Tuple[ActType], newActs: Tuple[ActType]) -> bool:
    # APEX をプレイしていたことを確認
    apexed = False
    for act in oldActs:
        if (isinstance(act, discord.Spotify)):
            continue
        if act.type == discord.ActivityType.playing and act.name == APEXGAME:
            apexed = True
            break
    if not apexed:
        return False
    
    # 今 APEX をプレイしていないことを確認
    for act in newActs:
        if (isinstance(act, discord.Spotify)):
            continue
        if act.type == discord.ActivityType.playing and act.name == APEXGAME:
            return False
    return True

@client.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    logging.debug(f'member update ${str(before)} ${after}')
    
    started = apex_started(before.activities, after.activities)
    stopped = apex_stopped(before.activities, after.activities)
    if not started and not stopped:
        logging.debug("not related to apex")
        return
    
    await _send_apex_notification(after, APEXGAME, started)


client.run(TOKEN)
