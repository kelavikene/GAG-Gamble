# Commands Folder

This folder contains all the command modules for your Discord bot.

## File Structure

Organize your commands by category:
```commands/
├── admin/          # Admin-only commands
├── moderation/     # Moderation commands
├── fun/            # Entertainment commands
├── utility/        # Utility commands
├── music/          # Music-related commands
└── economy/        # Economy/game commands
```

## Command File Example

Each command file should typically follow this structure:
```python
import discord
from discord.ext import commands

class CommandName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='example')
    async def example_command(self, ctx):
        """Example command description"""
        await ctx.send("Hello World!")

def setup(bot):
    bot.add_cog(CommandName(bot))
```

## Loading Commands

Load commands in your main bot file using:
```python
# Load all commands from a category
for filename in os.listdir('./commands/category'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.category.{filename[:-3]}')
```