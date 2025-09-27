"""
Discord integration for mastication pipeline.
Uses Discord HTTP API for reactions and message sending.
"""

import os
import logging
import requests
import json
from datetime import datetime
from pathlib import Path


class DiscordClient:
    """Simple Discord client using HTTP API"""

    def __init__(self):
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
        }

        # Channel IDs - these need to be configured
        self.classifications_channel_id = os.getenv(
            "DISCORD_CLASSIFICATIONS_CHANNEL_ID"
        )
        self.fodder_channel_id = os.getenv("DISCORD_FODDER_CHANNEL_ID")
        self.guild_id = os.getenv("DISCORD_GUILD_ID")

        self.initialized = bool(self.token)

    def get_message_id_from_filename(self, filename):
        """Extract Discord message ID from filename"""
        try:
            # Remove file extension and extract message ID
            message_id = Path(filename).stem
            # Validate that it's a valid Discord message ID (numeric)
            if message_id.isdigit():
                return int(message_id)
        except (ValueError, AttributeError):
            pass
        return None

    def add_thinking_reaction(self, file_path):
        """Add thinking emoji reaction to the original Discord message"""
        if not self.initialized:
            return False

        try:
            message_id = self.get_message_id_from_filename(Path(file_path).name)
            if not message_id:
                logging.warning(
                    f"Could not extract message ID from filename: {file_path}"
                )
                return False

            # Add thinking reaction to the message in the fodder channel
            if self.fodder_channel_id:
                url = f"{self.base_url}/channels/{self.fodder_channel_id}/messages/{message_id}/reactions/%F0%9F%A4%94/@me"
                response = requests.put(url, headers=self.headers)

                if response.status_code == 204:
                    logging.info(f"Added thinking reaction to message {message_id}")
                    return True
                else:
                    logging.warning(
                        f"Failed to add thinking reaction: {response.status_code} - {response.text}"
                    )
                    return False
            else:
                logging.warning(
                    "DISCORD_FODDER_CHANNEL_ID not configured - cannot add reactions\n"
                    "To enable Discord reactions, add DISCORD_FODDER_CHANNEL_ID to your .env file\n"
                    "Get the channel ID by enabling Developer Mode in Discord and right-clicking the channel"
                )
                return False

        except Exception as e:
            logging.error(f"Error adding thinking reaction: {e}")
            return False

    def update_reaction_and_notify(
        self, file_path, success=True, response=None, error=None
    ):
        """Update reaction and send notification to classifications channel"""
        if not self.initialized:
            return False

        try:
            message_id = self.get_message_id_from_filename(Path(file_path).name)
            if not message_id:
                logging.warning(
                    f"Could not extract message ID from filename: {file_path}"
                )
                return False

            # Remove thinking reaction and add result reaction
            if self.fodder_channel_id:
                # Remove thinking reaction
                remove_url = f"{self.base_url}/channels/{self.fodder_channel_id}/messages/{message_id}/reactions/%F0%9F%A4%94/@me"
                requests.delete(remove_url, headers=self.headers)

                # Add result reaction
                if success:
                    reaction_emoji = "%F0%9F%9A%80"  # 🚀
                else:
                    reaction_emoji = "%E2%9D%8C"  # ❌

                add_url = f"{self.base_url}/channels/{self.fodder_channel_id}/messages/{message_id}/reactions/{reaction_emoji}/@me"
                response_react = requests.put(add_url, headers=self.headers)

                if response_react.status_code == 204:
                    logging.info(f"Updated reaction for message {message_id}")
                else:
                    logging.warning(
                        f"Failed to update reaction: {response_react.status_code}"
                    )
            else:
                logging.warning(
                    "DISCORD_FODDER_CHANNEL_ID not configured - cannot update reactions\n"
                    "To enable Discord reactions, add DISCORD_FODDER_CHANNEL_ID to your .env file\n"
                    "Get the channel ID by enabling Developer Mode in Discord and right-clicking the channel"
                )

            # Send notification to classifications channel
            if self.classifications_channel_id:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if success:
                    status = "Success"
                    title = "**Classification Success** 🚀"

                    if response and isinstance(response, dict):
                        # Create clickable message link if guild ID is available
                        message_link = (
                            f"https://discord.com/channels/{self.guild_id}/{self.fodder_channel_id}/{message_id}"
                            if self.guild_id and self.fodder_channel_id
                            else f"Message ID: {message_id}"
                        )

                        # Extract classification data
                        category = response.get("category", "Unknown")
                        confidence = response.get("confidence", 0.0)
                        summary = response.get("summary", "No summary available")
                        subcategory = response.get("subcategory")
                        tags = response.get("tags", [])

                        # Format confidence as percentage
                        confidence_pct = f"{confidence * 100:.1f}%"

                        # Build formatted message
                        content_parts = [
                            f"{title}",
                            f"**Original Message:** {message_link}",
                            f"**Timestamp:** {timestamp}",
                            "---",
                            f"**Category:** {category}",
                            f"**Confidence:** {confidence_pct}",
                        ]

                        if subcategory:
                            content_parts.append(f"**Subcategory:** {subcategory}")

                        content_parts.extend(["", f"**Summary:** {summary}", ""])

                        if tags:
                            tags_str = ", ".join([f"`{tag}`" for tag in tags])
                            content_parts.append(f"**Tags:** {tags_str}")

                        content = "\n".join(content_parts)
                    else:
                        content = f"{title}\nOriginal message ID: {message_id}\nTimestamp: {timestamp}\n---\n*No response data available*"
                else:
                    status = "Fail"
                    title = "**Classification Fail** ❌"
                    error_msg = str(error) if error else "Unknown error"

                    if len(error_msg) > 1800:  # Leave room for message wrapper
                        error_msg = error_msg[:1800] + "... (truncated)"

                    content = f"{title}\nOriginal message ID: {message_id}\nTimestamp: {timestamp}\n---\n```\n{error_msg}\n```"

                # Send message to classifications channel
                url = f"{self.base_url}/channels/{self.classifications_channel_id}/messages"
                data = {"content": content}

                response_msg = requests.post(url, headers=self.headers, json=data)

                if response_msg.status_code == 200:
                    logging.info(f"Sent {status} notification for message {message_id}")
                    return True
                else:
                    logging.warning(
                        f"Failed to send notification: {response_msg.status_code} - {response_msg.text}"
                    )
                    return False
            else:
                logging.warning(
                    "DISCORD_CLASSIFICATIONS_CHANNEL_ID not configured - cannot send notifications\n"
                    "To enable Discord notifications, add these to your .env file:\n"
                    "- DISCORD_CLASSIFICATIONS_CHANNEL_ID\n"
                    "- DISCORD_FODDER_CHANNEL_ID  \n"
                    "- DISCORD_GUILD_ID\n"
                    "Get the IDs by enabling Developer Mode in Discord and right-clicking the respective channels/server"
                )
                return False

        except Exception as e:
            logging.error(f"Error in Discord notification: {e}")
            return False


# Global Discord client instance
discord_client = DiscordClient()
