import asyncio
import sys
import os
from typing import Dict, Any

# Ensure scripts module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from scripts.zai_token import DiscordOAuthHandler

async def login_with_discord_token(discord_token: str) -> Dict[str, Any]:
    """
    Asynchronously exchange Discord Token for Zai Access Token.
    """
    def _login():
        handler = DiscordOAuthHandler()
        return handler.backend_login(discord_token)
    
    # Run blocking synchronous code in a separate thread
    return await asyncio.to_thread(_login)