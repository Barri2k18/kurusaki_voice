import discord
import asyncio
import platform
import colorsys
import youtube_dl
import os
import time
import random
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import find
from discord import Game, Embed, Color, Status, ChannelType

BOT_PREFIX = ("+", "a!", "ax", "366579653395349505", "<@366579653395349505>")

bot=commands.Bot(command_prefix=BOT_PREFIX)

from discord import opus
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

owner = "362672438699622403"

def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
load_opus_lib()

in_voice=[]


players = {}
songs = {}
playing = {}


async def all_false():
    for i in bot.servers:
        playing[i.id]=False


async def checking_voice(ctx):
    await asyncio.sleep(130)
    if playing[ctx.message.server.id]== False:
        try:
            pos = in_voice.index(ctx.message.server.id)
            del in_voice[pos]
            server = ctx.message.server
            voice_client = bot.voice_client_in(server)
            await voice_client.disconnect()
            await bot.say("{} left because there was no audio playing for a while".format(bot.user.name))
        except:
            pass

@bot.event
async def on_ready():
    bot.loop.create_task(all_false())
    print(bot.user.name)    
    
@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await bot.join_voice_channel(channel)
    in_voice.append(ctx.message.server.id)


async def player_in(con):  # After function for music
    try:
        if len(songs[con.message.server.id]) == 0:  # If there is no queue make it False
            playing[con.message.server.id] = False
            bot.loop.create_task(checking_voice(con))
    except:
        pass
    try:
        if len(songs[con.message.server.id]) != 0:  # If queue is not empty
            # if audio is not playing and there is a queue
            songs[con.message.server.id][0].start()  # start it
            await bot.send_message(con.message.channel, 'Now queueed')
            del songs[con.message.server.id][0]  # delete list afterwards
    except:
        pass
        
@bot.command(pass_context=True, hidden=True)
async def setavatar(ctx, url):
	if ctx.message.author.id not in owner:
		return
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as r:
			data = await r.read()
	await bot.edit_profile(avatar=data)
	await bot.say("I changed my avatar.", delete_after=6)
	await bot.delete_message(ctx.message)



  	
@bot.command(pass_context=True, hidden=True)
async def setgame(ctx, *, game):
    if ctx.message.author.id not in owner:
        return
    game = game.strip()
    if game != "":
        try:
            await bot.change_presence(game=discord.Game(name=game))
        except:
            await bot.say("Failed to change game")
        else:
            await bot.say("Successfuly changed game to {}".format(game))
    else:
        await bot.send_cmd_help(ctx)

@bot.command(pass_context=True, hidden=True)
async def setname(ctx, *, name):
    if ctx.message.author.id not in owner:
        return
    name = name.strip()
    if name != "":
        try:
            await bot.edit_profile(username=name)
        except:
           await bot.say("Failed to change name")
        else:
            await bot.say("Successfuly changed name to {}".format(name))
    else:
        await bot.send_cmd_help(ctx)
        await bot.delete_message(ctx.message)
	
@bot.command(pass_context=True)
async def avatar(ctx, member: discord.Member):
	embed = discord.Embed(title="{}'s avatar".format(member.name), url=member.avatar_url)
	embed.set_image(url=member.avatar_url)
	embed.set_footer(text='{}'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
	await bot.delete_message(ctx.message)
	await bot.say(embed=embed) # ----------------------------------- EMBED ONE
      
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def say(ctx, *, msg = None):
    await bot.delete_message(ctx.message)
    if not msg: await bot.say("Please specify a message to send")
    else: await bot.say(msg)
    return

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def embed(ctx, *args):
    """
    Sending embeded messages with color (and maby later title, footer and fields)
    """
    argstr = " ".join(args)
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    text = argstr
    color = discord.Color((r << 16) + (g << 8) + b)
    await bot.send_message(ctx.message.channel, embed=Embed(color = color, description=text))
    await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def play(ctx, *,url):

    opts = {
        'default_search': 'auto',
        'quiet': True,
    }  # youtube_dl options


    if ctx.message.server.id not in in_voice: #auto join voice if not joined
        channel = ctx.message.author.voice.voice_channel
        await bot.join_voice_channel(channel)
        in_voice.append(ctx.message.server.id)

    

    if playing[ctx.message.server.id] == True: #IF THERE IS CURRENT AUDIO PLAYING QUEUE IT
        voice = bot.voice_client_in(ctx.message.server)
        song = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        songs[ctx.message.server.id]=[] #make a list 
        songs[ctx.message.server.id].append(song) #add song to queue
        await bot.say("Audio {} is queued".format(song.title))

    if playing[ctx.message.server.id] == False:
        voice = bot.voice_client_in(ctx.message.server)
        player = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        players[ctx.message.server.id] = player
        # play_in.append(player)
        if players[ctx.message.server.id].is_live == True:
            await bot.say("Can not play live audio yet.")
        elif players[ctx.message.server.id].is_live == False:
            player.start()
            await bot.say("Now playing audio")
            playing[ctx.message.server.id] = True



@bot.command(pass_context=True)
async def queue(con):
    await bot.say("There are currently {} audios in queue".format(len(songs)))

@bot.command(pass_context=True)
async def pause(ctx):
    players[ctx.message.server.id].pause()

@bot.command(pass_context=True)
async def resume(ctx):
    players[ctx.message.server.id].resume()
          
@bot.command(pass_context=True)
async def volume(ctx, vol:float):
    volu = float(vol)
    players[ctx.message.server.id].volume=volu


@bot.command(pass_context=True)
async def skip(con): #skipping songs?
  songs[con.message.server.id]
    
    
    
@bot.command(pass_context=True)
async def stop(con):
    players[con.message.server.id].stop()
    songs.clear()

@bot.command(pass_context=True)
async def leave(ctx):
    pos=in_voice.index(ctx.message.server.id)
    del in_voice[pos]
    server=ctx.message.server
    voice_client=bot.voice_client_in(server)
    await voice_client.disconnect()
    songs.clear()
    

bot.run(os.environ['BOT_TOKEN'])
