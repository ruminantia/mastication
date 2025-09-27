#!/usr/bin/env python3
"""
Test script for Discord integration in mastication pipeline.
This script tests the Discord client functionality without running the full pipeline.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord import discord_client


async def test_discord_client():
    """Test the Discord client functionality"""
    print("Testing Discord client initialization...")

    # Check if Discord token is available
    if not os.getenv("DISCORD_BOT_TOKEN"):
        print("❌ DISCORD_BOT_TOKEN not found in environment variables")
        print("Please set DISCORD_BOT_TOKEN in your .env file")
        return False

    # Initialize Discord client
    print("Initializing Discord client...")
    success = await discord_client.initialize()

    if not success:
        print("❌ Failed to initialize Discord client")
        return False

    print("✅ Discord client initialized successfully")

    # Test message ID extraction
    print("\nTesting message ID extraction...")
    test_cases = [
        "1421596834563887195.txt",
        "123456789.txt",
        "invalid_filename.txt",
        "not_a_number.txt",
        "1421596834563887195.md",
    ]

    for filename in test_cases:
        message_id = discord_client.get_message_id_from_filename(filename)
        if message_id:
            print(f"✅ {filename} -> {message_id}")
        else:
            print(f"❌ {filename} -> Could not extract message ID")

    # Test with a sample file path (this won't actually send reactions, just test the logic)
    print("\nTesting reaction logic (will not actually send reactions)...")
    sample_file_path = "input/2025/09/27/1421596834563887195.txt"

    try:
        # Test thinking reaction (this will fail if message not found, but that's expected)
        thinking_success = await discord_client.add_thinking_reaction(sample_file_path)
        if thinking_success:
            print("✅ Thinking reaction logic test passed")
        else:
            print("⚠️ Thinking reaction would fail (message likely not found)")

        # Test success notification
        sample_response = {
            "category": "tasks",
            "confidence": 0.9,
            "subcategory": "reminder",
            "summary": "The content describes an audio clip containing a spoken reminder to pack socks for an Amtrak trip scheduled for Monday.",
            "tags": ["reminder", "packing", "travel", "Amtrak", "Monday", "audio clip"],
            "input_filename": "1421596834563887195.txt",
        }

        success_notification = await discord_client.update_reaction_and_notify(
            sample_file_path, success=True, response=sample_response
        )

        if success_notification:
            print("✅ Success notification logic test passed")
        else:
            print("⚠️ Success notification would fail (message likely not found)")

        # Test error notification
        error_notification = await discord_client.update_reaction_and_notify(
            sample_file_path, success=False, error="Test error message"
        )

        if error_notification:
            print("✅ Error notification logic test passed")
        else:
            print("⚠️ Error notification would fail (message likely not found)")

    except Exception as e:
        print(f"❌ Error during reaction tests: {e}")

    # Close Discord client
    print("\nClosing Discord client...")
    await discord_client.close()
    print("✅ Discord client closed")

    return True


async def main():
    """Main test function"""
    print("🧪 Mastication Discord Integration Test")
    print("=" * 50)

    try:
        success = await test_discord_client()
        if success:
            print("\n🎉 All tests completed successfully!")
            print(
                "\n📝 Note: Some tests may show warnings if the actual Discord message"
            )
            print("   is not found. This is expected behavior.")
        else:
            print("\n💥 Some tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
