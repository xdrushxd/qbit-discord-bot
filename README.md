# Discord qBittorrent Status Bot

A Discord bot that displays and manages your qBittorrent downloads in real-time. The bot provides status updates, download management, and auto-refresh capabilities.

## Features

- **Real-time Status Updates**: Shows all active downloads with progress, speed, and ETA
- **Category Filtering**: Filter downloads by category (movies, TV shows, etc.)
- **Status Filtering**: Filter by download status (downloading, seeding, completed)
- **Auto-refresh Control**: Control status updates with emoji reactions
- **User-friendly Commands**: Simple commands with clear feedback
- **Multi-part Support**: Automatically splits long status messages
- **Error Handling**: Graceful error handling with user-friendly messages

## Commands

### Status Commands
- `$status` - Show all downloads
- `$status movies` - Show only movies
- `$status tv` - Show only TV shows
- `$status all downloading` - Show all downloading items
- `$status movies seeding` - Show seeding movies
- `$status tv completed` - Show completed TV shows
- `$help` - Show all available commands

### Auto-refresh Control
The status message includes two emoji reactions for controlling auto-refresh:
- ⏸️ (Pause) - Click to pause auto-refresh
- ▶️ (Play) - Click to resume auto-refresh

The status message footer shows the current auto-refresh state:
- "🔄 Auto-refresh enabled" when running
- "⏸️ Auto-refresh paused" when paused

## Setup

1. Clone this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration:
   ```
   BOT_CHANNEL=your_channel_id
   TV_CATEGORY=tv-sonarr
   MOVIE_CATEGORY=radarr
   QBIT_HOST=your_qbit_host
   QBIT_PORT=your_qbit_port
   QBIT_USERNAME=your_qbit_username
   QBIT_PASSWORD=your_qbit_password
   DISCORD_TOKEN=your_discord_token
   ```
4. Run the bot:
   ```bash
   python qbit_bot.py
   ```

## Requirements
- Python 3.8+
- discord.py
- qbittorrent-api
- python-dotenv

## Notes
- The bot automatically updates status messages every 5 minutes
- You can control auto-refresh using the ⏸️ and ▶️ emoji reactions
- Status messages are split into multiple parts if they exceed Discord's length limit
- The bot maintains category and status filters during auto-updates
- 
## 📸 Visual Preview  
 
 Get a glimpse of how the bot operates with these screenshots:  
 
 ### 🛠️ Help Command Execution  
 When the help command is triggered, users see a structured list of available commands:  
 ![Help](https://i.imgur.com/UsgSkvU.png)  
 
 ### 🖥️ Server Shell Output  
 Real-time execution logs displayed directly in the server terminal:  
 ![Shell](https://i.imgur.com/aJDLlU3.png)  
 
 ### 💬 Discord Channel Output  
 How the bot interacts within a Discord channel:  
 ![Channel](https://i.imgur.com/rSS5uga.png)  
