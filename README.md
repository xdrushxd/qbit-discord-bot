# QBit Torrent Discord Bot

A Discord bot that interfaces with qBittorrent to monitor and manage your torrents.

## Features

- Monitor torrent progress and status
- Filter torrents by category (movies/TV shows)
- View download speeds and estimated completion times
- Clean, formatted Discord messages with embeds
- Automatic message cleanup to avoid channel clutter

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 2.1 Create Discord bot
   ```
   Login to the discord developer website, create a new bot. (not going in detail)
   ````
3. Configure the `.env` file with your settings:
   ```
   BOT_CHANNEL=your_discord_channel_id
   TV_CATEGORY=your_tv_category
   MOVIE_CATEGORY=your_movie_category
   QBIT_HOST=your_qbittorrent_host
   QBIT_PORT=your_qbittorrent_port
   QBIT_USERNAME=your_qbittorrent_username
   QBIT_PASSWORD=your_qbittorrent_password
   DISCORD_TOKEN=your_discord_bot_token
   ```
4. Run the bot:
   ```bash
   python qbit_bot.py
   ```

## Usage

- `$status` - Show all torrents
- `$status movies` - Show movie torrents
- `$status tv` - Show TV show torrents
- `$status completed` - Show completed torrents
- `$status downloading` - Show downloading torrents
- `$help` - Show all available commands

You can combine filters, for example:
- `$status movies completed` - Show completed movie torrents
- `$status tv downloading` - Show downloading TV show torrents

## Features

- **Improved Error Handling**: Comprehensive error handling and logging
- **Security**: Sensitive information stored in environment variables
- **Clean Code**: Object-oriented design with clear separation of concerns
- **Better Formatting**: Rich Discord embeds for better readability
- **Performance**: Efficient filtering and sorting of torrent lists
- **Maintainability**: Well-documented code with clear structure 
