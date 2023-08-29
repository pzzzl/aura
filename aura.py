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

bot = commands.Bot(
    command_prefix=["aura ", "AURA ", "Aura", "aURA ", "arua "], intents=intents
)

QUEUE = []


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command()
async def ajuda(ctx):
    await ctx.send(
        "**Bem vindo ao Aura BOT**\n\nCOMANDOS\n\n• *join* | j\n• *disconnect* | dc, exit, quit, leave\n• *play* | p\n• *next* | n, skip, s\n• *queue* | q"
    )


@bot.command(aliases=["j"])
async def join(ctx):
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
    await ctx.send("Aura entrou no servidor.")


@bot.command(aliases=["exit", "quit", "dc", "disconnect"])
async def leave(ctx):
    await ctx.voice_client.disconnect()
    QUEUE.clear()
    await ctx.send("Aura saiu do servidor.")


@bot.command(aliases=["p"])
async def play(ctx, *, query):
    await ctx.send("Procurando...")
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

    if 'entries' in info:
        title = info['entries'][0]['title']
        duration = info['entries'][0]['duration']
    else:
        title = info['title']
        duration = info['duration']

    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)
    duration = f"{duration_minutes}:{duration_seconds}"

    

    QUEUE.append(url)
    if not voice_client.is_playing():
        await play_queue(ctx, voice_client, title, duration)


@bot.command(aliases=["next", "n", "s"])
async def skip(ctx):
    await ctx.send("Pulando música...")
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    if QUEUE:
        await play_queue(ctx, ctx.voice_client)


@bot.command(aliases=["q"])
async def queue(ctx):
    await ctx.send(QUEUE)


async def play_queue(ctx, voice_client, title = None, duration = None):
    if QUEUE:
        url = QUEUE.pop(0)
        if title:
            await ctx.send(f":notes: **{title}** `({duration})`")
        voice_client.stop()
        voice_client.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda e: bot.loop.create_task(play_queue(ctx, voice_client)),
        )


bot.run(variables.TOKEN)
