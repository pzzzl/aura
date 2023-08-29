import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import variables
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {
    "executable": variables.FFMPEG_EXECUTABLE_PATH,
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

bot = commands.Bot(command_prefix=["!"], intents=intents)

QUEUE = []
SPOTIPY_CLIENT_ID = variables.CLIENT_ID_SPOTIFY
SPOTIPY_CLIENT_SECRET = variables.CLIENT_SECRET_SPOTIFY
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))


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
    await ctx.send("Aura conectou ao servidor.")


@bot.command(aliases=["exit", "quit", "dc", "disconnect"])
async def leave(ctx):
    await ctx.voice_client.disconnect()
    QUEUE.clear()
    await ctx.send("Aura foi desconectado do servidor.")


@bot.command(aliases=["p"])
async def play(ctx, *, query):
    msg = await ctx.send("Procurando...")
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

    if "spotify.com" in query:
        # Extrair a ID da faixa do link do Spotify
        track_id = query.split("/")[-1].split("?")[0]
        print(track_id)
        try:
            track_info = sp.track(track_id)
            track_name = track_info["name"]
            query = track_name  # Usar o título da música como query
        except:
            await ctx.send(content="Não foi possível obter informações da faixa do Spotify. Você está tentando colocar uma playist? Pois se estiver, tenho uma má notícia...")
            return

    try:
        if "youtube.com" in query or "youtu.be" in query:
            info = ydl.extract_info(query, download=False)
            url = info["url"]
        else:
            query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)
            url = info["entries"][0]["url"]

        if "entries" in info:
            title = info["entries"][0]["title"]
            duration = info["entries"][0]["duration"]
        else:
            title = info["title"]
            duration = info["duration"]
    except:
        return await ctx.send("Música não encontrada.")

    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)
    duration = f"{duration_minutes}:{duration_seconds}"

    await msg.delete()

    msg = await ctx.send(f"Adicionado à fila: **{title}** `({duration})`")
    QUEUE.append({"url": url, "title": title, "duration": duration, "message": msg})
    if not voice_client.is_playing():
        await play_queue(ctx, voice_client)


@bot.command(aliases=["next", "n", "s"])
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()


@bot.command(aliases=["q"])
async def queue(ctx):
    count = 1
    out = ""
    if not QUEUE:
        await ctx.send(":x: Não há músicas na fila :x:")
    for obj in QUEUE:
        out = out + f"{count}. **{obj['title']}**\n"
        count = count + 1
    if out:
        await ctx.send(out)


async def play_queue(ctx, voice_client):
    if QUEUE:
        obj = QUEUE.pop(0)
        url = obj["url"]
        if obj["title"]:
            emoji = discord.PartialEmoji(name="aura_play", id=1145950272334614598)
            await obj["message"].delete()
            await ctx.send(f"{emoji} **{obj['title']}** `({obj['duration']})`")
        voice_client.stop()

        voice_client.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda e: bot.loop.create_task(play_queue(ctx, voice_client)),
        )
    else:
        await ctx.send("Reprodução finalizada.")


bot.run(variables.TOKEN)
