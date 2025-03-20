## install discord.py
## py -3 -m pip install -U discord.py

## install requests
## py -3 -m pip install -U requests

## install qbittorrent-api
## py -3 -m pip install -U qbittorrent-api

import discord
from discord.ext import commands
import requests
import qbittorrentapi
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import asyncio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
class Status:
    COMPLETED = "Completed"
    DOWNLOADING = "Downloading"
    MISSING = "Files missing"
    STALLED = "Stalled"
    STARTING = "Attempting to start"
    QUEUED = "Queued"
    PAUSED = "Paused"
    UNKNOWN = "Unknown status"

class Config:
    LIST_SEPARATOR = ",    "
    NOTHING_DOWNLOADING = "Nothing is downloading! Why not request something?"
    DOWNLOADING_STATUS = "downloading"
    COMPLETE_STATUS = "completed"
    MAX_DISCORD_CHARS = 1700

    @staticmethod
    def load_env():
        load_dotenv()
        return {
            'BOT_CHANNEL': os.getenv('BOT_CHANNEL'),
            'TV_CATEGORY': os.getenv('TV_CATEGORY', 'tv-sonarr'),
            'MOVIE_CATEGORY': os.getenv('MOVIE_CATEGORY', 'radarr'),
            'QBIT_HOST': os.getenv('QBIT_HOST'),
            'QBIT_PORT': os.getenv('QBIT_PORT'),
            'QBIT_USERNAME': os.getenv('QBIT_USERNAME'),
            'QBIT_PASSWORD': os.getenv('QBIT_PASSWORD'),
            'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN')
        }

class TorrentManager:
    def __init__(self, client):
        self.client = client
        self.status_map = {
            'uploading': Status.COMPLETED,
            'pausedUP': Status.COMPLETED,
            'checkingUP': Status.COMPLETED,
            'stalledUP': Status.COMPLETED,
            'forcedUP': Status.COMPLETED,
            'downloading': Status.DOWNLOADING,
            'missingFiles': Status.MISSING,
            'stalledDL': Status.STALLED,
            'metaDL': Status.STARTING,
            'queuedDL': Status.QUEUED,
            'pausedDL': Status.PAUSED
        }

    def get_torrent_list(self):
        try:
            torrent_list = []
            for torrent in self.client.torrents_info():
                torrent_list.append({
                    'name': torrent.name,
                    'category': torrent.category,
                    'progress': f"{round(torrent.progress*100,2)}%",
                    'state': self._map_state(torrent.state),
                    'eta': self._format_eta(torrent.eta),
                    'size': self._format_size(torrent.size),
                    'download_speed': self._format_speed(torrent.dlspeed)
                })
            return torrent_list
        except Exception as e:
            logger.error(f"Error getting torrent list: {str(e)}")
            return []

    def _map_state(self, state):
        return self.status_map.get(state, Status.UNKNOWN)

    def _format_eta(self, seconds):
        if seconds == 8640000:
            return "∞"
        
        intervals = [
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1)
        ]
        
        parts = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                name = name[:-1] if value == 1 else name
                parts.append(f"{value} {name}")
        
        return 'ETA: ' + ', '.join(parts[:2]) if parts else 'Done'

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def _format_speed(self, speed_bytes):
        return self._format_size(speed_bytes) + "/s"

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix='$',
            intents=intents,
            help_command=commands.DefaultHelpCommand(
                no_category="Available Commands",
                width=120,
                sort_commands=False
            )
        )
        
        # Load configuration
        self.config = Config.load_env()
        
        # Initialize qBittorrent client
        self.qbt_client = self._setup_qbit_client()
        self.torrent_manager = TorrentManager(self.qbt_client)

        # Register commands
        self.add_commands()

    def _setup_qbit_client(self):
        try:
            client = qbittorrentapi.Client(
                host=self.config['QBIT_HOST'],
                port=self.config['QBIT_PORT'],
                username=self.config['QBIT_USERNAME'],
                password=self.config['QBIT_PASSWORD']
            )
            client.auth_log_in()
            return client
        except Exception as e:
            logger.error(f"Failed to connect to qBittorrent: {str(e)}")
            raise

    def add_commands(self):
        @self.event
        async def on_ready():
            logger.info(f'Bot is ready: {self.user.name} ({self.user.id})')
            await self.change_presence(activity=discord.Game(name="Type $help for commands! 🤖"))

        @self.command(name='status', 
                     brief="📥 Check your torrent downloads",
                     help="""
🔍 **How to use the status command:**

1️⃣ Basic Usage:
   `$status` - Shows all your torrents

2️⃣ Filter by Category:
   `$status movies` - Shows only movie torrents
   `$status tv` - Shows only TV show torrents

3️⃣ Filter by Status:
   `$status completed` - Shows finished downloads
   `$status downloading` - Shows active downloads

4️⃣ Combine Filters:
   `$status movies completed` - Shows finished movie downloads
   `$status tv downloading` - Shows TV shows currently downloading

💡 **Tips:**
• Use `$status all` to see everything
• Downloads are automatically sorted by progress
• Each torrent shows:
  - Name
  - Progress percentage
  - Download speed
  - Estimated time remaining
  - File size

❓ Need more help? Just type `$help` for all commands!
""")
        async def status(ctx, category="all", status_filter="all"):
            if str(ctx.channel.id) != self.config['BOT_CHANNEL']:
                await ctx.send("❌ Oops! I can only respond to commands in the designated download status channel!")
                return

            try:
                # Clean up old messages
                await self._clean_channel(ctx)
                
                # Get and filter torrent list
                torrents = self.torrent_manager.get_torrent_list()
                filtered = self._filter_torrents(torrents, category, status_filter)
                
                if not filtered:
                    embed = discord.Embed(
                        title="No Downloads Found 🤔",
                        description="Nothing is downloading right now! Why not request something new? 🎬",
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    return

                # Format and send messages
                messages = self._format_for_discord(filtered)
                for i, msg in enumerate(messages, 1):
                    embed = discord.Embed(
                        title=f"Download Status {f'(Part {i}/{len(messages)})' if len(messages) > 1 else ''}",
                        description=msg,
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text="🔄 Updates automatically | 💾 Powered by r-lab.ovh")
                    await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Error in status command: {str(e)}")
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Oops! Something went wrong: {str(e)}\nPlease try again later or contact the admin if this persists.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

        @self.command(name='help_downloads',
                     brief="📚 Learn how to use the download status bot",
                     help="""
🤖 **Welcome to the Download Status Bot!**

This bot helps you keep track of your downloads from qBittorrent. Here's how to use it:

📋 **Basic Commands:**
1. `$status` - Shows all your downloads
2. `$help` - Shows this help message

🎯 **Filtering Downloads:**
• By Category:
  `$status movies` - Only movie downloads
  `$status tv` - Only TV show downloads

• By Status:
  `$status completed` - Finished downloads
  `$status downloading` - Active downloads

• Combined:
  `$status movies completed` - Finished movies
  `$status tv downloading` - TV shows in progress

📊 **Understanding the Status:**
• Each download shows:
  - 📝 Name of the file
  - 📈 Progress percentage
  - ⚡ Download speed
  - ⏱️ Time remaining
  - 💾 File size

💡 **Tips:**
• Messages update automatically
• Old messages are cleaned up
• Downloads are sorted by progress
• Use emojis to quickly identify status

❓ **Need Help?**
If something's not working, contact the admin!
""")
        async def help_downloads(ctx):
            if str(ctx.channel.id) != self.config['BOT_CHANNEL']:
                await ctx.send("❌ Oops! I can only respond to commands in the designated download status channel!")
                return

            embed = discord.Embed(
                title="📚 Download Status Bot Help",
                description=self.get_command('help_downloads').help,
                color=discord.Color.blue()
            )
            embed.set_footer(text="🤖 Type $status to check your downloads!")
            await ctx.send(embed=embed)

    async def _clean_channel(self, ctx):
        def not_pinned(message):
            return not message.pinned
        await ctx.channel.purge(check=not_pinned)

    def _filter_torrents(self, torrents, category, status_filter):
        filtered = []
        for torrent in torrents:
            if (category == "all" or torrent['category'] == category) and \
               (status_filter == "all" or 
                (status_filter == "completed" and torrent['state'] == Status.COMPLETED) or
                (status_filter == "downloading" and torrent['state'] != Status.COMPLETED)):
                filtered.append(torrent)
        
        # Sort by progress
        return sorted(filtered, key=lambda x: float(x['progress'][:-1]), reverse=True)

    def _format_for_discord(self, torrents):
        messages = []
        current_msg = ""
        
        for torrent in torrents:
            # Add emoji based on status
            status_emoji = "✅" if torrent['state'] == Status.COMPLETED else "⏳"
            
            entry = (
                f"**{torrent['name']}** {status_emoji}\n"
                f"▫️ Progress: `{torrent['progress']}` | Status: `{torrent['state']}`\n"
                f"▫️ Size: `{torrent['size']}` | Speed: `{torrent['download_speed']}`\n"
                f"▫️ {torrent['eta']}\n\n"
            )
            
            if len(current_msg) + len(entry) > Config.MAX_DISCORD_CHARS:
                messages.append(current_msg)
                current_msg = entry
            else:
                current_msg += entry
        
        if current_msg:
            messages.append(current_msg)
        
        return messages

def main():
    try:
        bot = DiscordBot()
        bot.run(bot.config['DISCORD_TOKEN'])
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise

if __name__ == "__main__":
    main()