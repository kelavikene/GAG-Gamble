import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class BankingSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/banking.json'
        self.load_banking_data()
    
    def load_banking_data(self):
        """Load banking data from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.banking_data = json.load(f)
        except FileNotFoundError:
            self.banking_data = {
                'banker_roles': {},  # guild_id: role_id
                'hub_messages': {},  # guild_id: {'channel_id': channel_id, 'message_id': message_id}
                'settings': {},      # guild_id: {'deposit_enabled': True, 'withdraw_enabled': True}
            }
            self.save_banking_data()
    
    def save_banking_data(self):
        """Save banking data to file"""
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.banking_data, f, indent=2)
    
    def load_emojis(self):
        """Load emojis from emojis.json"""
        try:
            with open('emojis.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    async def create_bank_hub_embed(self, guild_id):
        """Create the bank hub embed"""
        emojis = self.load_emojis()
        
        # Get banking emojis
        bank_emoji = emojis.get('banking', {}).get('bank', '🏦')
        deposit_emoji = emojis.get('banking', {}).get('deposite_up', '⬆️')
        withdraw_emoji = emojis.get('banking', {}).get('withdraw_down', '⬇️')
        
        embed = discord.Embed(
            title=f"{bank_emoji} Bank Status",
            description="Here you can deposit and withdraw your in-game items!",
            color=0x0099ff  # Blue color
        )
        
        # Add deposit and withdraw fields with just emojis
        embed.add_field(
            name=f"**Depositing:** {deposit_emoji}",
            value="\u200b",
            inline=True
        )
        
        embed.add_field(
            name=f"**Withdrawing:** {withdraw_emoji}",
            value="\u200b",
            inline=True
        )
        
        embed.add_field(name="\u200b", value="Use buttons below to proceed.", inline=False)
        
        # Set the image
        embed.set_image(url="https://cdn.discordapp.com/attachments/1390659613447426089/1390659694711930981/Screenshot_20250703_211651.jpg?ex=686b0a84&is=6869b904&hm=16fca25314000b7e44a2a8871fbb195a6b5d68cd911bed25956444a9118c07fc&")
        
        return embed
    
    def create_bank_buttons(self, guild_id):
        """Create the deposit/withdraw buttons"""
        emojis = self.load_emojis()
        settings = self.banking_data['settings'].get(str(guild_id), {'deposit_enabled': True, 'withdraw_enabled': True})
        
        view = discord.ui.View(timeout=None)
        
        # Deposit button
        deposit_emoji = emojis.get('banking', {}).get('deposite_up', '⬆️')
        deposit_button = discord.ui.Button(
            label="Deposit",
            emoji=deposit_emoji,
            style=discord.ButtonStyle.grey,
            disabled=not settings['deposit_enabled'],
            custom_id=f"bank_deposit_{guild_id}"
        )
        
        # Withdraw button
        withdraw_emoji = emojis.get('banking', {}).get('withdraw_down', '⬇️')
        withdraw_button = discord.ui.Button(
            label="Withdraw", 
            emoji=withdraw_emoji,
            style=discord.ButtonStyle.grey,
            disabled=not settings['withdraw_enabled'],
            custom_id=f"bank_withdraw_{guild_id}"
        )
        
        view.add_item(deposit_button)
        view.add_item(withdraw_button)
        
        return view
    
    @app_commands.command(name="setuphub", description="Setup the banking hub (Admin only)")
    @app_commands.describe(channel="The channel to send the banking hub message")
    async def setup_hub(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check if user is admin (fix for Member vs User issue)
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
            return
        
        try:
            # Create embed and buttons
            embed = await self.create_bank_hub_embed(interaction.guild.id)
            view = self.create_bank_buttons(interaction.guild.id)
            
            # Send the message
            message = await channel.send(embed=embed, view=view)
            
            # Save hub message info
            guild_id = str(interaction.guild.id)
            self.banking_data['hub_messages'][guild_id] = {
                'channel_id': channel.id,
                'message_id': message.id
            }
            
            # Initialize settings if not exist
            if guild_id not in self.banking_data['settings']:
                self.banking_data['settings'][guild_id] = {
                    'deposit_enabled': True,
                    'withdraw_enabled': True
                }
            
            self.save_banking_data()
            
            await interaction.response.send_message(f"✅ Banking hub has been set up in {channel.mention}!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error setting up hub: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="setbanker", description="Set the banker role (Admin only)")
    @app_commands.describe(role="The role to set as banker")
    async def set_banker(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user is admin (fix for Member vs User issue)
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            self.banking_data['banker_roles'][guild_id] = role.id
            self.save_banking_data()
            
            await interaction.response.send_message(f"✅ Banker role has been set to {role.mention}!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error setting banker role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="bankerconsole", description="Banker control panel (Banker/Admin only)")
    async def banker_console(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        
        # Check permissions (fix for Member vs User issue)
        is_admin = interaction.user.guild_permissions.administrator if hasattr(interaction.user, 'guild_permissions') else False
        banker_role_id = self.banking_data['banker_roles'].get(guild_id)
        is_banker = False
        
        if banker_role_id and hasattr(interaction.user, 'roles'):
            is_banker = banker_role_id in [role.id for role in interaction.user.roles]
        
        if not (is_admin or is_banker):
            await interaction.response.send_message("❌ You need to be an administrator or have the banker role to use this command!", ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title="🏦 Banker Control Panel",
                description="Use the dropdowns below to control the banking system:",
                color=0x0099ff
            )
            
            # Get current settings
            settings = self.banking_data['settings'].get(guild_id, {'deposit_enabled': True, 'withdraw_enabled': True})
            
            deposit_status = "✅ Enabled" if settings['deposit_enabled'] else "❌ Disabled"
            withdraw_status = "✅ Enabled" if settings['withdraw_enabled'] else "❌ Disabled"
            
            embed.add_field(name="💰 Deposit Status", value=deposit_status, inline=True)
            embed.add_field(name="💸 Withdraw Status", value=withdraw_status, inline=True)
            
            view = BankerControlView(self, guild_id)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error opening banker console: {str(e)}", ephemeral=True)
    
    async def update_hub_message(self, guild_id):
        """Update the hub message with new settings"""
        try:
            hub_info = self.banking_data['hub_messages'].get(str(guild_id))
            if not hub_info:
                return
            
            channel = self.bot.get_channel(hub_info['channel_id'])
            if not channel:
                return
            
            message = await channel.fetch_message(hub_info['message_id'])
            if not message:
                return
            
            # Update embed and buttons
            embed = await self.create_bank_hub_embed(guild_id)
            view = self.create_bank_buttons(guild_id)
            
            await message.edit(embed=embed, view=view)
        
        except Exception as e:
            print(f"Error updating hub message: {e}")

class BankerControlView(discord.ui.View):
    def __init__(self, cog, guild_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id
        
        # Load emojis
        emojis = self.cog.load_emojis()
        up_emoji = emojis.get('banking', {}).get('deposite_up', '⬆️')
        down_emoji = emojis.get('banking', {}).get('withdraw_down', '⬇️')
    
    @discord.ui.select(
        placeholder="🏦 Deposit Control",
        options=[
            discord.SelectOption(label="Enable Deposit", value="deposit_enable", emoji="⬆️"),
            discord.SelectOption(label="Disable Deposit", value="deposit_disable", emoji="⬇️")
        ]
    )
    async def deposit_control(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            guild_id = str(self.guild_id)
            
            if guild_id not in self.cog.banking_data['settings']:
                self.cog.banking_data['settings'][guild_id] = {'deposit_enabled': True, 'withdraw_enabled': True}
            
            if select.values[0] == "deposit_enable":
                self.cog.banking_data['settings'][guild_id]['deposit_enabled'] = True
                status = "✅ enabled"
            else:
                self.cog.banking_data['settings'][guild_id]['deposit_enabled'] = False
                status = "❌ disabled"
            
            self.cog.save_banking_data()
            await self.cog.update_hub_message(self.guild_id)
            
            await interaction.response.send_message(f"💰 Deposit has been {status}!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.select(
        placeholder="💸 Withdraw Control",
        options=[
            discord.SelectOption(label="Enable Withdraw", value="withdraw_enable", emoji="⬆️"),
            discord.SelectOption(label="Disable Withdraw", value="withdraw_disable", emoji="⬇️")
        ]
    )
    async def withdraw_control(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            guild_id = str(self.guild_id)
            
            if guild_id not in self.cog.banking_data['settings']:
                self.cog.banking_data['settings'][guild_id] = {'deposit_enabled': True, 'withdraw_enabled': True}
            
            if select.values[0] == "withdraw_enable":
                self.cog.banking_data['settings'][guild_id]['withdraw_enabled'] = True
                status = "✅ enabled"
            else:
                self.cog.banking_data['settings'][guild_id]['withdraw_enabled'] = False
                status = "❌ disabled"
            
            self.cog.save_banking_data()
            await self.cog.update_hub_message(self.guild_id)
            
            await interaction.response.send_message(f"💸 Withdraw has been {status}!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BankingSetup(bot))