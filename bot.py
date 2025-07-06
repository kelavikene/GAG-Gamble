import discord
from discord.ext import commands
import json
import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found!")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json!")
        return None

config = load_config()
if not config:
    exit(1)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=config['discord']['prefix'],
    intents=intents,
    help_command=None
)

# Event handlers
@bot.event
async def on_ready():
    print(f'🤖 Bot is ready!')
    print(f'📝 Logged in as: {bot.user.name}')
    print(f'🆔 Bot ID: {bot.user.id}')
    print(f'🌐 Connected to {len(bot.guilds)} servers')
    print(f'👥 Watching {len(set(bot.get_all_members()))} users')
    print('─' * 50)
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name=f"{config['discord']['prefix']}help | Ready to serve!")
    )

@bot.event
async def on_member_join(member):
    if config['settings']['welcomeMessage']:
        try:
            channel = discord.utils.get(member.guild.channels, name='general')
            if channel:
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=f"Welcome to **{member.guild.name}**, {member.mention}!",
                    color=int(config['colors']['success'].replace('#', ''), 16)
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending welcome message: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param}`")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error in command {ctx.command}: {error}")

# Basic Commands
@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: `{latency}ms`",
        color=int(config['colors']['info'].replace('#', ''), 16)
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=int(config['colors']['info'].replace('#', ''), 16)
    )
    embed.add_field(name="👤 Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="🌐 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=len(set(bot.get_all_members())), inline=True)
    embed.add_field(name="📝 Prefix", value=config['discord']['prefix'], inline=True)
    embed.add_field(name="🐍 Python", value="discord.py", inline=True)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="📚 Bot Commands",
        description="Here are the available commands:",
        color=int(config['colors']['info'].replace('#', ''), 16)
    )
    
    commands_list = [
        ("🏓 `!ping`", "Check bot latency"),
        ("ℹ️ `!info`", "Show bot information"),
        ("📚 `!help`", "Show this help message"),
        ("👋 `!hello`", "Say hello to the bot"),
        ("🎲 `!roll [sides]`", "Roll a dice (default 6 sides)"),
        ("💎 `!serverinfo`", "Show server information")
    ]
    
    for name, value in commands_list:
        embed.add_field(name=name, value=value, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='hello')
async def hello(ctx):
    """Say hello"""
    responses = [
        f"Hello {ctx.author.mention}! 👋",
        f"Hi there, {ctx.author.display_name}! 😊",
        f"Hey {ctx.author.mention}! How are you doing? 🎉"
    ]
    import random
    await ctx.send(random.choice(responses))

@bot.command(name='roll')
async def roll_dice(ctx, sides: int = 6):
    """Roll a dice"""
    if sides < 2:
        await ctx.send("❌ Dice must have at least 2 sides!")
        return
    if sides > 100:
        await ctx.send("❌ Dice can't have more than 100 sides!")
        return
    
    import random
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"You rolled a **{result}** on a {sides}-sided dice!",
        color=int(config['colors']['success'].replace('#', ''), 16)
    )
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def server_info(ctx):
    """Show server information"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"🏰 {guild.name}",
        color=int(config['colors']['info'].replace('#', ''), 16)
    )
    
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📝 Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    await ctx.send(embed=embed)

# Load commands from commands folder
def load_extensions():
    """Load command extensions from the commands folder"""
    if not os.path.exists('commands'):
        print("Commands folder not found, skipping extension loading.")
        return
    
    for filename in os.listdir('commands'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                bot.load_extension(f'commands.{filename[:-3]}')
                print(f"✅ Loaded extension: {filename}")
            except Exception as e:
                print(f"❌ Failed to load extension {filename}: {e}")

# Main execution
async def main():
    print("🚀 Starting Discord Bot...")
    print("📁 Loading extensions...")
    load_extensions()
    
    try:
        print("🔗 Connecting to Discord...")
        await bot.start(config['discord']['token'])
    except discord.LoginFailure:
        print("❌ Invalid bot token! Please check your config.json")
    except discord.HTTPException as e:
        print(f"❌ HTTP Exception: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown requested by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
