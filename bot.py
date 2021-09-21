#!/bin/python
import os
import discord
import threading
import random
import asyncio
import youtube_dl
import subprocess
import sys

from dotenv import load_dotenv
from discord.ext import commands

# Load .env files.
load_dotenv()

client = commands.Bot(command_prefix="!")

class mainvariables():
    # * STRINGS * #
    music_base_dir = "/home/nytri/Music/fav"
    """Base directory for musics."""
    musics = os.listdir("/home/nytri/Music/fav")
    """ Music selection list."""
    ffmpeg_path = "/usr/bin/ffmpeg"
    """ FFMpeg executable location"""
    music_playing = str()
    """ This is the name of the music file."""
    music_playing_fullpath = str()
    """ Full path of the music file, used for arguments to play the music in this path."""
    user_homedir = "/home/nytri"
    # * LISTS * #
    shuffled_music_ids = list()
    """Used for shuffling the music"""
    music_played = []
    """Music Played"""


mainvars = mainvariables()


class connection():
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    async def checkIfBotVoiceChannelConnected(self):
        """Check if the bot is connected to the VOICE CHANNEL.

        Returns:
            Boolean: If the bot is not connected to the VOICE CHANNEL then return False.
        """
        try:
            if discord.utils.get(self.ctx.guild.voice_channels, name="Music"):
                return True
            else:
                self.ctx.send("Bot Voice Channel function returns false")
                return False
        except discord.ClientException:
            return True
    
    async def checkifBotVoiceConnected(self):
        """Check if the bot is connected to the VOICE CHAT.

        Returns:
            Boolean: If the bot is not connected to the VOICE CHAT then return False.
        """
        voice = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        if voice == None:
            return False
        else:
            if voice.is_connected():
                return True
            else:
                return False
        
    
    async def checkVoiceConnections(self):
        """Check if the bot is already connected to the VOICE CHANNEL and VOICE CHAT.
        if not then returns False.
        if yes then returns True.

        Returns:
            Boolean: If the bot is not connected to the channel and voice chat then returns False.
        """
        if await self.checkIfBotVoiceChannelConnected():
            voice = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
            if voice == None:
                return False
            else:
                return True
        else:
            await self.ctx.send("Bot not connected to channel.")
            return False
        
    async def connectVoiceChat(self):
        """Connect the bot to the VOICE CHAT. If the bot is not connected to the VOICE CHAT 
        then the function will use discord library to connect to the VOICE CHAT\n
        \n
        If the bot is already connected to the VOICE CHAT then the function will pass.
        Returns:
            Boolean: Returns True if the bot managed to connect to the VOICE CHAT else returns False.
        """
        if not self.checkifBotVoiceConnected:
            if discord.utils.get(client.voice_clients, guild=self.ctx.guild).connect():
                return True
            else:
                return False
        else:
            pass
            
        
    async def connectAll(self):
        """Connect the bot to the Music Channel.
        Automatically checks if the bot is already connected to the channel.

        Returns:
            [Boolean]: [False] if the bot is already connected to the channel.
        
        If the bot is already connected to the channel then returns True.
        """
        if await self.checkIfBotVoiceChannelConnected():
            if not await self.checkIfBotVoiceChannelConnected():
                try:
                    await discord.utils.get(self.ctx.guild.voice_channels, name="Music").connect()
                    await discord.utils.get(discord.voice_client, guild=self.ctx.guild).connect()
                except discord.ClientException:
                    pass
                return True
            else:
                try:
                    await discord.utils.get(self.ctx.guild.voice_channels, name="Music").connect()
                except discord.ClientException:
                    pass
                return True
        else:
            await self.ctx.send("Returns False")
            return False                      
                
        
    async def connectBotVoiceChannel(self):
        """Connect the bot to the Voice Channel.

        Returns:
            Boolean: If the bot managed to connect to the voice channel then returns True.
        """
        voice_channel = discord.utils.get(self.ctx.guild.voice_channels, name="Music")
        if voice_channel:
            await voice_channel.connect()
            return True
        else:
            # * Connect to voice channel.
            #  await voice_channel.connect()
            return False
        
    async def getBotVoiceChat(self):
        """Return the VOICE CHAT object.

        Returns:
            Discord: Returns VOICE CHAT voice object. If none then return None.
        """
        if await self.checkIfBotVoiceChannelConnected():
            return discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        else:
            return None
    
    async def reconnectBotVoice(self):
        """Reconnect the bot to the voice channel and voice chat
        """
        voiceChannel = discord.utils.get(self.ctx.guild.voice_channels, name="Music")
        voiceChat = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        # * Disconnect VOICE CHANNEL and VOICE CHAT
        voiceChannel.disconnect()
        voiceChat.disconnect()
        # * Connect VOICE CHANNEL and VOICE CHAT
        voiceChannel.connect()
        voiceChat.connect()


class discord_Music():
    def __init__(self, ctx):
        self.con = connection(ctx)
        self.ctx = ctx
    
    async def play(self, filename: str, name: str):
        """Play the music provided in arguments.

        Args:
            filename (str): Path of the music file to play.
            name (str): Name of the music to play.
            \n
            examples of name arguments:
            * If the filename arguments is Music.mp3 then the name of the music will be Music. It will remove the extension at the end.
        """
        voice = await self.con.getBotVoiceChat()
        if voice:
            mainvars.music_playing = str(name)
            mainvars.music_playing_fullpath = str(filename)
            if voice.is_playing():
                voice.stop()
                voice.play(discord.FFmpegPCMAudio(source=filename))
            else:
                voice.play(discord.FFmpegPCMAudio(source=filename))
        else:
            await self.con.connectVoiceChat()
            voice = await self.con.getBotVoiceChat()
            mainvars.music_playing = str(name)
            mainvars.music_playing_fullpath = str(filename)
            voice.play(discord.FFmpegPCMAudio(source=filename))
        
    async def stop(self):
        """Stop the music.

        Returns:
            Boolean: Returns False if there is no music currently playing.
        """
        voice = await self.con.getBotVoiceChat()
        if voice.is_playing():
            voice.stop()
            return True
        else:
            return False
    
    async def pause(self):
        """Pause the music playing.

        Returns:
            Boolean: Returns False if the music is not playing or the music is already paused.
        """
        voice = await self.con.getBotVoiceChat()
        if voice.is_playing():
            if voice.is_paused():
                return False
            else:
                voice.pause()
                return True
        else:
            return False
    
    async def resume(self):
        """Resume music paused by the user

        Returns:
            Boolean: Return False if the music is currently playing or the music is not paused.
        """
        voice = await self.con.getBotVoiceChat()
        if voice.is_playing():
            return False
        else:
            if voice.is_paused():
                voice.resume()
                return True
            else:
                return False
        

class redirector():
    def __init__(self, ctx):
        self.ctx = ctx
        self.con = connection(ctx)
        self.discordMusic = discord_Music(ctx)

    async def random(self):
        """Shuffle all music in list of mainvars.musics list.
        """
        await self.con.connectAll()
        if await self.con.checkIfBotVoiceChannelConnected():
            voice = await self.con.getBotVoiceChat()
            # * Add the music id's to the list.
            ids = []
            for id in range(1, len(mainvars.musics)):
                ids.append(id)
            # * Shuffle music id's
            mainvars.shuffled_music_ids = random.sample(ids, k=len(mainvars.musics) -1)
            i = random.sample(mainvars.shuffled_music_ids, k=1)
            await self.discordMusic.play("{}/{}".format(mainvars.music_base_dir, mainvars.musics[i[0]]), mainvars.musics[i[0]])
            

    
    async def stop(self):
        """Stop the music currently playing
        """
        if await self.con.checkifBotVoiceConnected():
            if await self.discordMusic.stop():
                pass
            else:
                await self.ctx.send("No music playing.")
        else:
            await self.ctx.send("No music playing.")
    
    async def pause(self):
        """Pause the music currently playing"""
        if await self.con.checkifBotVoiceConnected():
            if await self.discordMusic.pause():
                pass
            else:
                await self.ctx.send("The music is already paused or there is no music playing.")
        else:
            await self.ctx.send("No music playing.")
    
    async def resume(self):
        """Resume the music currently playing"""
        if await self.con.checkifBotVoiceConnected():
            if await self.discordMusic.resume():
                pass
            else:
                await self.ctx.send("No music playing or the music is not paused.")
        else:
            await self.ctx.send("No music playing.")
            
    async def restart(self):
        """Restart the music currently playing"""
        if await self.con.checkifBotVoiceConnected():
            if mainvars.music_playing == "" and mainvars.music_playing_fullpath == "":
                await self.ctx.send("No music currently playing.")
            else:
                await self.ctx.send("Restarting {}".format(mainvars.music_playing.replace(".mp3", "")))
                await self.discordMusic.stop()
                await self.discordMusic.play(mainvars.music_playing_fullpath, mainvars.music_playing)
        else:
            await self.ctx.send("Bot is not connected to the Voice Chat.")
                


@client.command()
@commands.has_any_role("administrators")
async def music_random(ctx):
    m = redirector(ctx)
    await m.random()


@client.command()
@commands.has_any_role("administrators")
async def music_stop(ctx):
    m = redirector(ctx)
    await m.stop()
    

@client.command()
@commands.has_any_role("administrators")
async def music_pause(ctx):
    m = redirector(ctx)
    await m.pause()

@client.command()
@commands.has_any_role("administrators")
async def music_resume(ctx):
    m = redirector(ctx)
    await m.resume()

@client.command()
@commands.has_any_role("administrators")
async def music_restart(ctx):
    m = redirector(ctx)
    await m.restart()

@client.command(pass_context=True)
@commands.has_any_role("administrators")
async def music_list(ctx):
    count = 0
    musics_string_list = str()
    while count < len(mainvars.musics):
        if len(musics_string_list) >= 1800:
            await ctx.send(musics_string_list)
            musics_string_list = ""
        else:
            musics_string_list += "%s) %s\n" % (count + 1, mainvars.musics[count])
        count += 1
    await ctx.send(musics_string_list)


@client.command()
@commands.has_any_role("administrators")
async def music_sel(ctx, id: int):
    m = redirector(ctx)
    discordMusic = discord_Music(ctx)
    con = connection(ctx)
    
    music_name = mainvars.musics[id - 1]
    music_full_path = "{}/{}".format(mainvars.music_base_dir, mainvars.musics[id - 1])
    # * Ensure that the bot is connected to the music channel.
    await con.connectAll()
    if await con.checkIfBotVoiceChannelConnected():
        await discordMusic.play(music_full_path, music_name)


@client.command()
@commands.has_any_role("administrators")
async def music_youtube(ctx, url: str):
    # * Set youtubedl headers
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    yt_title = str()
    yt_id = str()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([str(url)])
        infos = ydl.extract_info([str(url)])
        yt_title = infos.get("title")
        yt_id = infos.get("id")
    await ctx.send("%s : %s" % (yt_title, yt_id)) 

    
print("Bot %s successfully logged in." % client.user)


# * CHANGE IT TO YOUR BOT TOKEN.
client.run(os.environ["TOKEN"])