###########
## SETUP ##
###########
import os
from time import time, sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import discord
from youtubesearchpython.__future__ import *
from youtubesearchpython.internal.constants import ResultMode
from discord.ext import commands
from pytube import *
import asyncio
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "!", intents = intents)
stop_b = False
skip_b = False
query = []
titles = []


@client.event
async def on_ready():
    print('Muse Bot is ready.')

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Hey there! I\'m Muse. I\'m currently just a simple music bot that uses only music available on YouTube!')
        break

@client.command(pass_context=True)
async def musehelp(ctx):
    await ctx.send('')

@client.command(pass_context=True)
async def p(ctx, *, args):
    global query
    user = ctx.message.author
    
    isPlaylist = False
    
    if(user.voice == None):
        await ctx.send('You must be in a voice channel to play the bot!')
        return
    vc = user.voice.channel
    
    # Search for video or use argument if link is provided
    if args.startswith('https://www.youtube.com/playlist') or  args.startswith('http://youtube.com/playlist'):
        links = await searchPlaylist(ctx, args)
        isPlaylist = True
    elif args.startswith('https://') or args.startswith('youtube.com') or args.startswith('www.'):
        link = await searchVidLink(ctx, args)
    else:
        link = await searchVid(ctx, args)

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice == None and isPlaylist == False:
        query.insert(0, link)
        await ctx.send(f"Joined **{vc}**")
        vc = await vc.connect()
        await downloadPop(ctx, vc)
    elif voice == None and isPlaylist == True:
        for link in links:
            query.insert(0, link)
        await ctx.send(f"Joined **{vc}** and queued **Playlist of {len(links)} songs**")
        vc = await vc.connect()
        await downloadPop(ctx, vc)
    elif isPlaylist == True:
        for link in links:
            query.insert(0, link)
        await ctx.send(f"Queued **Playlist of {len(links)} songs**")
    else:
        query.insert(0, link)
        await ctx.send(f"Queued **{titles[0]}**")

async def searchVid(ctx, args):
    from youtubesearchpython.__future__ import Video
    videosSearch = VideosSearch(args, limit = 1)
    videoResult = await videosSearch.next()
    link = videoResult["result"][0]
    titles.insert(0, link["title"])
    return link["link"]

async def searchVidLink(ctx, args):
    from youtubesearchpython import Video
    videosSearch = Video.get(args, mode = ResultMode.json)
    videoResult = videosSearch
    titles.insert(0, videoResult["title"])
    return args

async def searchPlaylist(ctx, args):
    from youtubesearchpython.extras import Playlist
    links = []
    playlist = Playlist.get(args, mode = ResultMode.dict)
    for video in (playlist["videos"]):
        links.append(video["link"])
        titles.insert(0,video["title"])
    return links

    # print(f'Videos Retrieved: {len(playlist["videos"])}')
def clearQ():
    global query
    global titles
    query = []
    titles = []

async def downloadPop(ctx, vc):
    FFMPEG_OPTIONS = {
        'options': '-vn',
    }
    global query
    global stop_b
    if len(titles) > 0:
        title = titles[len(titles) - 1]
    if len(query) > 0:
        link = query.pop()
        title = titles.pop()
        yt = YouTube(link)
        ys = yt.streams.filter(only_audio=True)[0]
        ys.download(output_path = 'E:/MusicBot/temp_muse/', filename = 'current_song.mp3')
        await ctx.send(f"Now playing **{title}**")
        vc.play(discord.FFmpegPCMAudio(source='E:/MusicBot/temp_muse/current_song.mp3', **FFMPEG_OPTIONS), after=lambda e: os.remove("E:/MusicBot/temp_muse/current_song.mp3"))
    while vc.is_playing():
        await asyncio.sleep(1)
        global skip_b
        if (skip_b == True or stop_b == True):
            if skip_b == True:
                await ctx.send(f"Skipping **{title}**")
            skip_b = False
            vc.stop()
    
    if len(query) > 0 and stop_b == False:
        await downloadPop(ctx, vc)
    elif stop_b == True:
        await ctx.send(f"Disconnecting!")
        stop_b = False 
        clearQ()
    await asyncio.sleep(2)
    await vc.disconnect()

@client.command(pass_context=True)
async def skip(ctx):
    global skip_b
    skip_b = True

@client.command(pass_context=True)
async def stop(ctx):
    global stop_b
    stop_b = True

client.run('ODg5NjExMjE0NDU4NTk3NDA3.YUjxAQ.qwSrxiEObnh85T-XvmbVWJNjmOo')
