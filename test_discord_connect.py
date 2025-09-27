#!/usr/bin/env python3
"""
Simple test script to verify Discord client connection.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord import discord_client


async def test_discord_connection():
    """Test Discord client connection"""
    print("🧪 Testing Discord client connection...")

    # Check if Discord token is available
    if not os.getenv("DISCORD_BOT_TOKEN"):
        print("❌ DISCORD_BOT_TOKEN not found in environment variables")
        return False

    print("🔑 Discord token found")

    try:
        # Initialize Discord client
        print("🔄 Initializing Discord client...")
        success = await discord_client.initialize()

        if not success:
            print("❌ Failed to initialize Discord client")
            return False

        print("✅ Discord client initialized successfully")

        # Check if client is connected
        if discord_client.client and discord_client.client.is_ready():
            print(f"🤖 Connected as: {discord_client.client.user}")
            print(f"🏠 Connected to {len(discord_client.client.guilds)} guild(s)")

            # List available channels
            for guild in discord_client.client.guilds:
                print(f"  📋 Guild: {guild.name} (ID: {guild.id})")
                for channel in guild.text_channels:
                    print(f"    📝 Channel: {channel.name} (ID: {channel.id})")

        # Test message ID extraction
        print("\n🔍 Testing message ID extraction...")
        test_cases = [
            ("1421605101063376998.txt", 1421605101063376998),
            ("123456789.txt", 123456789),
            ("invalid.txt", None),
            ("not_a_number.txt", None),
        ]

        for filename, expected in test_cases:
            result = discord_client.get_message_id_from_filename(filename)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {filename} -> {result} (expected: {expected})")

        # Close connection
        print("\n🔌 Closing Discord client...")
        await discord_client.close()
        print("✅ Discord client closed")

        return True

    except Exception as e:
        print(f"❌ Error during Discord connection test: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 Mastication Discord Connection Test")
    print("=" * 50)

    try:
        success = await test_discord_connection()
        if success:
            print("\n🎉 Discord connection test passed!")
        else:
            print("\n💥 Discord connection test failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
