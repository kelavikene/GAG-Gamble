#!/usr/bin/env python3
import json
import os
import subprocess
import sys

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_bot_process():
    print_header("🤖 BOT PROCESS STATUS")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        bot_processes = [line for line in result.stdout.split('\n') if 'python3 bot.py' in line and 'grep' not in line]
        
        if bot_processes:
            print("✅ Bot is RUNNING!")
            for process in bot_processes:
                parts = process.split()
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                print(f"   📊 Process ID: {pid} | CPU: {cpu}% | Memory: {mem}%")
        else:
            print("❌ Bot is NOT running!")
            return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False
    return True

def check_config():
    print_header("⚙️ CONFIGURATION STATUS")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Config file loaded successfully!")
        print(f"   🔑 Token: {'Set' if config.get('discord', {}).get('token') else 'Missing'}")
        print(f"   📝 Prefix: {config.get('discord', {}).get('prefix', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def check_banking_system():
    print_header("🏦 BANKING SYSTEM STATUS")
    try:
        if os.path.exists('data/banking.json'):
            with open('data/banking.json', 'r') as f:
                banking_data = json.load(f)
            
            print("✅ Banking system initialized!")
            print(f"   🏛️ Banker roles configured: {len(banking_data.get('banker_roles', {}))}")
            print(f"   📨 Hub messages active: {len(banking_data.get('hub_messages', {}))}")
            print(f"   ⚙️ Server settings: {len(banking_data.get('settings', {}))}")
            
            # Show settings for each server
            for guild_id, settings in banking_data.get('settings', {}).items():
                deposit_status = "✅" if settings.get('deposit_enabled') else "❌"
                withdraw_status = "✅" if settings.get('withdraw_enabled') else "❌"
                print(f"     Server {guild_id}: Deposit {deposit_status} | Withdraw {withdraw_status}")
            
        else:
            print("⚠️ Banking system not initialized yet")
            return False
    except Exception as e:
        print(f"❌ Banking system error: {e}")
        return False
    return True

def check_commands():
    print_header("📝 COMMANDS STATUS")
    try:
        if os.path.exists('commands/setup.py'):
            print("✅ Banking commands file exists!")
            
            with open('commands/setup.py', 'r') as f:
                content = f.read()
            
            commands = ['setuphub', 'setbanker', 'bankerconsole']
            for cmd in commands:
                if f'name="{cmd}"' in content:
                    print(f"   ✅ /{cmd} - Defined")
                else:
                    print(f"   ❌ /{cmd} - Missing")
        else:
            print("❌ Commands file missing!")
            return False
    except Exception as e:
        print(f"❌ Commands check error: {e}")
        return False
    return True

def check_emojis():
    print_header("😀 EMOJIS STATUS")
    try:
        with open('emojis.json', 'r') as f:
            emojis = json.load(f)
        
        print("✅ Emojis file loaded!")
        banking_emojis = emojis.get('banking', {})
        print(f"   🏦 Banking emojis: {len(banking_emojis)}")
        print(f"   ⬆️ Deposit emoji: {banking_emojis.get('deposite_up', 'Missing')}")
        print(f"   ⬇️ Withdraw emoji: {banking_emojis.get('withdraw_down', 'Missing')}")
        return True
    except Exception as e:
        print(f"❌ Emojis error: {e}")
        return False

def main():
    print("🔍 DISCORD BOT STATUS CHECKER")
    print("Checking all components...")
    
    checks = [
        check_bot_process(),
        check_config(),
        check_banking_system(),
        check_commands(),
        check_emojis()
    ]
    
    print_header("📊 SUMMARY")
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Your Discord bot is ready to use!")
        print("\n📋 Available Commands:")
        print("   /setuphub #channel    - Setup banking hub (Admin only)")
        print("   /setbanker @role      - Set banker role (Admin only)")
        print("   /bankerconsole        - Simple up/down control panel")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("❌ Some issues detected - check the details above")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()