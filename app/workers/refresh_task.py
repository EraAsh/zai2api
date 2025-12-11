import asyncio
import logging
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.account import Account
from app.services.token_manager import refresh_account_token, get_token_hash, get_zai_token_key
from app.db.redis import get_redis
from app.core.config import settings

logger = logging.getLogger(__name__)

async def check_and_refresh_tokens():
    """
    Periodic task to check for expiring tokens and refresh them.
    """
    logger.debug("Starting token refresh check")
    
    redis = await get_redis()
    
    async with SessionLocal() as session:
        # Get all active accounts
        stmt = select(Account).where(Account.is_active == True)
        result = await session.execute(stmt)
        accounts = result.scalars().all()
        
        for account in accounts:
            token_hash = get_token_hash(account.discord_token)
            key = get_zai_token_key(token_hash)
            
            # Check TTL
            ttl = await redis.ttl(key)
            
            # If key doesn't exist (ttl=-2) or expiring soon (< 10 mins)
            # -2: key does not exist
            # -1: key exists but no expiry (should not happen for tokens)
            if ttl < settings.ZAI_TOKEN_TTL_BUFFER:
                logger.info(f"Token for account {account.id} is expiring (TTL: {ttl}s) or missing. Refreshing...")
                
                # Try to acquire a lock for this account to avoid double refresh
                lock_key = f"zai:refresh_lock:{token_hash}"
                acquired = await redis.set(lock_key, "locked", ex=60, nx=True)
                
                if acquired:
                    try:
                        await refresh_account_token(session, account)
                    except Exception as e:
                        logger.error(f"Error refreshing token for account {account.id}: {e}")
                    finally:
                        await redis.delete(lock_key)
                else:
                    logger.debug(f"Refresh lock active for account {account.id}, skipping.")
            else:
                pass
                # logger.debug(f"Token for account {account.id} is valid (TTL: {ttl}s)")

# Scheduler setup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(check_and_refresh_tokens, 'interval', seconds=settings.TOKEN_REFRESH_INTERVAL)
    scheduler.start()
    logger.info("Token refresh scheduler started")