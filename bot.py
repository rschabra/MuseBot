###########
## SETUP ##
###########
import os
import werkzeug
import ntpath
from time import time, sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import math
from datetime import datetime, timedelta
import sched
import requests
import discord
from youtubesearchpython.__future__ import *
import uuid
from discord.ext import commands
from pytube import *
import ffmpeg
import asyncio
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "!", intents = intents)
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
    
    
    if(user.voice == None):
        await ctx.send('You must be in a voice channel to play the bot!')
        return
    vc = user.voice.channel
    link = await searchVid(ctx, args)

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice == None:
        query.insert(0, link)
        await ctx.send(f"Joined **{vc}**")
        vc = await vc.connect()
        await downloadPop(ctx, vc)
    else:
        query.insert(0, link)
        await ctx.send(f"Queued **{titles[0]}**")

async def searchVid(ctx, args):
    videosSearch = VideosSearch(args, limit = 1)
    videoResult = await videosSearch.next()
    link = videoResult["result"][0]
    titles.insert(0, link["title"])
    return link["link"]

def clearQ():
    global query
    query = []

async def downloadPop(ctx, vc):
    FFMPEG_OPTIONS = {
        'options': '-vn',
    }
    global query
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
        if (skip_b == True):
            await ctx.send(f"Skipping **{title}**")
            skip_b = False
            vc.stop()
    if len(query) > 0:
        await downloadPop(ctx, vc)
    await asyncio.sleep(2)
    await vc.disconnect()

@client.command(pass_context=True)
async def skip(ctx):
    global skip_b
    skip_b = True


client.run('ODg5NjExMjE0NDU4NTk3NDA3.YUjxAQ.hcfPrLsebeE_ctDmpl2hUkjhfAE')
