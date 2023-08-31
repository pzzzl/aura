import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import variables
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
FFMPEG_OPTIONS = {
    "executable": variables.FFMPEG_EXECUTABLE_PATH,
    "before_options": variables.FFMPEG_BEFORE_OPTIONS,
    "options": variables.FFMPEG_OPTIONS,
}
bot = commands.Bot(command_prefix=variables.PREFIX, intents=intents)
QUEUE = []
SPOTIPY_CLIENT_ID = variables.CLIENT_ID_SPOTIFY
SPOTIPY_CLIENT_SECRET = variables.CLIENT_SECRET_SPOTIFY
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
    )
)


@bot.command()
async def enviar_imagem_aleatoria(ctx):
    image_paths = [variables.PATH_AJUSTES_1, variables.PATH_AJUSTES_2]
    chosen_image_path = random.choice(image_paths)
    with open(chosen_image_path, "rb") as image_file:
        await ctx.send(file=discord.File(image_file, "imagem.png"))


@bot.command()
async def fix(ctx):
    user_id_permitido = variables.USER_ID_PERMITIDO
    if ctx.author.id == user_id_permitido:
        await ctx.message.delete()
        await enviar_imagem_aleatoria(ctx)
        await ctx.send("Aura BOT está offline para manutenção.")
        exit()
    else:
        await ctx.send("Desculpe, você não tem permissão para executar este comando.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    channel_id = variables.CHANNEL_ID
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send("Aura BOT está online.")
    else:
        print(f"Canal com ID {channel_id} não encontrado.")


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


def extract_track_info(info):
    if "entries" in info:
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]
        duration = info["entries"][0]["duration"]
    else:
        url = info["url"]
        title = info["title"]
        duration = info["duration"]
    duration_minutes = int(duration // 60)
    duration_seconds = int(duration % 60)
    duration = f"{duration_minutes}:{duration_seconds}"
    msg = f"Adicionado à fila: **{title}** `({duration})`"
    return {"url": url, "title": title, "duration": duration, "message": msg}


async def add_music_to_queue(ctx, info):
    obj = extract_track_info(info)

    obj["message"] = await ctx.send(obj["message"])
    QUEUE.append(obj)


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
    try:
        # Se for uma track do Spotify
        if "spotify.com" in query and not "/playlist/" in query:
            track_id = query.split("/")[-1].split("?")[0]
            track_info = sp.track(track_id)
            track_name = track_info["name"]
            track_artist = track_info["artists"][0]["name"]
            query = f"ytsearch:{track_name} - {track_artist}"
            info = ydl.extract_info(query, download=False)
        # Se for uma playlist do Spotify
        elif "spotify.com" in query and "/playlist/" in query:
            await ctx.send("A reprodução de playlists do Spotify está desabilitada.")
            return
        # Se for um link do YouTube
        elif ("youtube.com" in query or "youtu.be" in query) and (
            not "playlist" in query
        ):
            info = ydl.extract_info(query, download=False)
        # Se for uma playlist do YouTube
        elif ("youtube.com" in query or "youtu.be" in query) and ("playlist" in query):
            await ctx.send("A reprodução de playlists do YouTube está desabilitada.")
            return
        # Se for uma pesquisa por texto
        else:
            query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)
    except:
        return await ctx.send("Música não encontrada.")
    # Deleta a mensagem "Procurando..."
    await msg.delete()
    await add_music_to_queue(ctx, info)
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
            emoji = discord.PartialEmoji(
                name=variables.PLAY_EMOJI_NAME, id=variables.PLAY_EMOJI_ID
            )
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
