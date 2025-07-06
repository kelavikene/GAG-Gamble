import discord
from discord.ext import commands
import json
import os
import asyncio
import logging
from datetime import datetime

# Console styling
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                     🤖 DISCORD BOT STARTING                 ║
║                         Version 1.0                         ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            print(f"{Colors.GREEN}✅ Configuration loaded successfully{Colors.RESET}")
            return config
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Error: config.json not found!{Colors.RESET}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.RED}❌ Error: Invalid JSON in config.json!{Colors.RESET}")
        return None

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler('data/bot.log'),
            logging.StreamHandler()
        ]
    )

# Load configuration
print_banner()
config = load_config()
if not config:
    print(f"{Colors.RED}❌ Failed to load configuration. Exiting...{Colors.RESET}")
    exit(1)

# Setup logging
os.makedirs('data', exist_ok=True)
setup_logging()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=config['discord']['prefix'],
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 BOT SUCCESSFULLY CONNECTED! 🎉{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}📝 Bot Name:{Colors.RESET} {Colors.YELLOW}{bot.user.name}{Colors.RESET}")
    print(f"{Colors.BOLD}🆔 Bot ID:{Colors.RESET} {Colors.YELLOW}{bot.user.id}{Colors.RESET}")
    print(f"{Colors.BOLD}🌐 Connected Servers:{Colors.RESET} {Colors.YELLOW}{len(bot.guilds)}{Colors.RESET}")
    print(f"{Colors.BOLD}👥 Total Users:{Colors.RESET} {Colors.YELLOW}{len(set(bot.get_all_members()))}{Colors.RESET}")
    print(f"{Colors.BOLD}📝 Command Prefix:{Colors.RESET} {Colors.YELLOW}{config['discord']['prefix']}{Colors.RESET}")
    print(f"{Colors.BOLD}⏰ Connected At:{Colors.RESET} {Colors.YELLOW}{current_time}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    # List connected servers
    if bot.guilds:
        print(f"{Colors.BOLD}🏰 Connected Servers:{Colors.RESET}")
        for guild in bot.guilds:
            print(f"   • {Colors.GREEN}{guild.name}{Colors.RESET} ({guild.member_count} members)")
    
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    
    # Sync slash commands
    try:
        print(f"{Colors.BLUE}🔄 Syncing slash commands...{Colors.RESET}")
        synced = await bot.tree.sync()
        print(f"{Colors.GREEN}✅ Synced {len(synced)} slash commands{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to sync commands: {e}{Colors.RESET}")
    
    print(f"{Colors.GREEN}✅ Bot is ready and waiting for commands!{Colors.RESET}\n")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name=f"{config['discord']['prefix']}help | Banking System Active"),
        status=discord.Status.online
    )

@bot.event
async def on_guild_join(guild):
    print(f"{Colors.GREEN}🎉 Joined new server: {Colors.YELLOW}{guild.name}{Colors.RESET} ({guild.member_count} members)")

@bot.event
async def on_guild_remove(guild):
    print(f"{Colors.RED}👋 Left server: {Colors.YELLOW}{guild.name}{Colors.RESET}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    else:
        print(f"{Colors.RED}❌ Error in command {ctx.command}: {error}{Colors.RESET}")

async def load_extensions():
    """Load command extensions from the commands folder"""
    if not os.path.exists('commands'):
        print(f"{Colors.YELLOW}📁 Commands folder not found, skipping extension loading.{Colors.RESET}")
        return
    
    print(f"{Colors.BLUE}📁 Loading command extensions...{Colors.RESET}")
    loaded = 0
    failed = 0
    
    for filename in os.listdir('commands'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f"   {Colors.GREEN}✅ Loaded: {filename}{Colors.RESET}")
                loaded += 1
            except Exception as e:
                print(f"   {Colors.RED}❌ Failed to load {filename}: {e}{Colors.RESET}")
                failed += 1
    
    print(f"{Colors.BLUE}📊 Extensions loaded: {Colors.GREEN}{loaded} successful{Colors.RESET}, {Colors.RED}{failed} failed{Colors.RESET}")

async def main():
    print(f"{Colors.BLUE}🚀 Initializing Discord Bot...{Colors.RESET}")
    await load_extensions()
    
    try:
        print(f"{Colors.BLUE}🔗 Connecting to Discord...{Colors.RESET}")
        await bot.start(config['discord']['token'])
    except discord.LoginFailure:
        print(f"{Colors.RED}❌ Invalid bot token! Please check your config.json{Colors.RESET}")
    except discord.HTTPException as e:
        print(f"{Colors.RED}❌ HTTP Exception: {e}{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Bot shutdown requested by user.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
    finally:
        if not bot.is_closed():
            await bot.close()
        print(f"{Colors.CYAN}👋 Bot has been shut down gracefully.{Colors.RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Bot shutdown requested.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
