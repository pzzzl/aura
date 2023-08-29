import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import variables

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {
    "executable": variables.FFMPEG_EXECUTABLE_PATH,
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

bot = commands.Bot(command_prefix="aura ", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)


@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@bot.command()
async def play(ctx, *, query):
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
        voice_client = ctx.voice_client
    else:
        voice_client = ctx.voice_client

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    if "youtube.com" in query or "youtu.be" in query:
        info = ydl.extract_info(query, download=False)
        url = info["url"]
    else:
        query = f"ytsearch:{query}"
        info = ydl.extract_info(query, download=False)
        url = info["entries"][0]["url"]

    voice_client.stop()

    voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))


bot.run(variables.TOKEN)
