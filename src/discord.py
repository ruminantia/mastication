import os
import discord
from datetime import datetime
import re

from src.transcriber import Transcriber
from src.audio_utils import chunk_audio

# Discord bot token loaded from environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Configure Discord intents to allow message content access
intents = discord.Intents.default()
intents.message_content = True

# Initialize Discord client with configured intents
client = discord.Client(intents=intents)

# Initialize the audio transcriber
transcriber = Transcriber()


@client.event
async def on_ready():
    """Handler for when the bot successfully connects to Discord."""
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    """
    Handler for incoming Discord messages.

    Processes audio attachments in the #fodder channel by:
    1. Downloading the audio file
    2. Chunking long audio files
    3. Transcribing with context-aware prompts
    4. Saving transcriptions locally
    5. Posting results to #transcriptions channel
    6. Adding reaction emojis to indicate status
    7. Cleaning up temporary files
    """
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Only process messages in the dedicated #fodder channel
    if message.channel.name != "fodder":
        return

    # Process any audio attachments in the message
    if message.attachments:
        for attachment in message.attachments:
            # Verify this is an audio file before processing
            if attachment.content_type and attachment.content_type.startswith("audio/"):
                try:
                    # Add processing reaction
                    await message.add_reaction("⏳")  # Hourglass emoji

                    # Download the audio file to local storage
                    audio_path = f"downloads/{attachment.filename}"
                    if not os.path.exists("downloads"):
                        os.makedirs("downloads")
                    await attachment.save(audio_path)

                    # Split audio into manageable chunks if it's too long
                    chunks = chunk_audio(audio_path)

                    # Transcribe all chunks with context passing between them
                    full_transcription = await transcriber.transcribe_chunks(chunks)

                    # Save transcription to file with message ID and date-based structure
                    now = datetime.now()
                    year = now.strftime("%Y")
                    month = now.strftime("%m")
                    day = now.strftime("%d")

                    # Create year/month/day directory structure
                    output_dir = f"fodder/{year}/{month}/{day}"
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    # Use original message ID as filename
                    output_filename = f"{output_dir}/{message.id}.txt"

                    with open(output_filename, "w") as f:
                        f.write(full_transcription)

                    # Find the transcriptions channel
                    transcriptions_channel = discord.utils.get(
                        message.guild.text_channels, name="transcriptions"
                    )

                    if not transcriptions_channel:
                        # Fallback: use the original channel if transcriptions channel doesn't exist
                        transcriptions_channel = message.channel
                        print(
                            "Warning: #transcriptions channel not found, using #fodder channel"
                        )

                    # Create a reference to the original message
                    original_message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

                    # Handle Discord's 2000-character message limit
                    if len(full_transcription) > 2000:
                        # Smart splitting that preserves chunk numbering structure
                        max_content_length = 2000  # Full Discord character limit

                        messages = []
                        current_message = ""

                        # Split by chunk boundaries to maintain numbering context
                        chunk_pattern = r"(?=\(\d+/\d+\))"
                        text_chunks = re.split(chunk_pattern, full_transcription)
                        text_chunks = [
                            chunk.strip() for chunk in text_chunks if chunk.strip()
                        ]

                        if text_chunks:
                            # Group chunks together when they fit within the limit
                            for chunk in text_chunks:
                                if (
                                    len(current_message) + len(chunk) + 1
                                    <= max_content_length
                                ):
                                    if current_message:
                                        current_message += " " + chunk
                                    else:
                                        current_message = chunk
                                else:
                                    # Start new message when current one would exceed limit
                                    if current_message:
                                        messages.append(current_message)
                                    current_message = chunk

                                    # Handle individual chunks that are too large
                                    if len(current_message) > max_content_length:
                                        # Split oversized chunk across multiple messages
                                        chunk_messages = [
                                            current_message[i : i + max_content_length]
                                            for i in range(
                                                0,
                                                len(current_message),
                                                max_content_length,
                                            )
                                        ]
                                        messages.extend(chunk_messages[:-1])
                                        current_message = chunk_messages[-1]

                            # Don't forget the last message
                            if current_message:
                                messages.append(current_message)
                        else:
                            # Fallback: simple character-based splitting
                            messages = [
                                full_transcription[i : i + max_content_length]
                                for i in range(
                                    0, len(full_transcription), max_content_length
                                )
                            ]

                        # Send header message with original message reference
                        await transcriptions_channel.send(
                            f"**Transcription from {message.author.display_name}**\n"
                            f"Original message: {original_message_link}\n"
                            f"Audio file: {attachment.filename}\n"
                            f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"---"
                        )

                        # Send all message parts to transcriptions channel
                        for i, msg_content in enumerate(messages, 1):
                            if i == 1:
                                # First part includes the header
                                await transcriptions_channel.send(
                                    f"```\n{msg_content}\n```"
                                )
                            else:
                                await transcriptions_channel.send(
                                    f"```\nPart {i}:\n{msg_content}\n```"
                                )
                    else:
                        # Single message fits within Discord's limit
                        await transcriptions_channel.send(
                            f"**Transcription from {message.author.display_name}**\n"
                            f"Original message: {original_message_link}\n"
                            f"Audio file: {attachment.filename}\n"
                            f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"---\n"
                            f"```\n{full_transcription}\n```"
                        )

                    # Clean up temporary files to prevent disk space accumulation
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                    if os.path.exists("temp_chunks"):
                        for chunk_path in chunks:
                            if os.path.exists(chunk_path):
                                os.remove(chunk_path)

                    # Remove processing reaction and add success reaction
                    await message.remove_reaction("⏳", client.user)
                    await message.add_reaction("✅")  # Checkmark emoji

                except Exception as e:
                    # Handle any errors during audio processing
                    print(f"Error processing audio attachment: {e}")

                    # Remove processing reaction and add error reaction
                    try:
                        await message.remove_reaction("⏳", client.user)
                        await message.add_reaction("❌")  # Red X emoji
                    except Exception:
                        pass  # Ignore errors with reactions if they occur

                    # Send error message to the original channel
                    await message.channel.send(
                        f"Sorry, there was an error processing the audio file: {str(e)}"
                    )
