<h1 align='center'>Aura BOT</h1>

<p align="center">
<img src='https://img.shields.io/badge/Status-pending_modifications-orange'>
<img src='https://img.shields.io/badge/BOT-Discord-purple'>
<img src='https://img.shields.io/badge/Feature-YouTube-red'>
<img src='https://img.shields.io/badge/Feature-Spotify-green'>
</p>

<p align='center'>Aura BOT is a Discord music bot developed in Python using the `discord.py` library.</p>

## Key Features

- Playback of `YouTube` music.
- Support for `Spotify` tracks.
- Commands to manage the playback queue.
- Basic interactions like joining and leaving a voice channel.

## How to Use

1. **Environment Setup:**
   - Ensure you have Python installed on your machine.
   - Install dependencies by running `pip install -r requirements.txt`.

2. **Discord Token Configuration:**
   - Obtain a Discord bot token [here](https://discord.com/developers/applications).
   - Fill in the `TOKEN` variable into the `variables.py` file.

3. **Spotify Configuration:**
   - Get Spotify client credentials [here](https://developer.spotify.com/dashboard/applications).
   - Fill in the `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` variables in `variables.py`.

4. **FFMPEG Configuration:**
   - Download FFMPEG [here](https://ffmpeg.org/download.html) and provide the executable path in `variables.py`.

5. **Running the Bot:**
   - Execute the bot using the command `python bot.py`.

## Commands

- `!play <query>`: Adds a song to the playback queue.
- `!skip`: Skips to the next song in the queue.
- `!queue`: Displays the playback queue.
- `!join`: Connects the bot to the voice channel.
- `!leave`: Disconnects the bot from the voice channel.

## Contribution

Contributions are welcome! If you find any issues or have suggestions, open an [issue](https://github.com/pzzzl/aura/issues) or submit a pull request.

## Author

### Bruno Peselli
