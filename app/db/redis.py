
from redis.asyncio import RedisError # type: ignore
import redis.asyncio as redis # type: ignore
from ..core.config import setting
from datetime import timedelta
from fastapi import HTTPException, status
from typing import Optional



class RedisManager:
  def __init__(self, redis_config: dict):
    """Initialize Redis connection with configuration."""
    self.redis = redis.Redis(
      host=redis_config.get('host'),
      port=redis_config.get('port'),
      password=redis_config.get('password'),
      ssl=redis_config.get('ssl', False)
    )

    self.REFRESH_TOKEN_PREFIX = "refresh_token:"
    self.BLACKLIST_SET = "blacklist"

  async def _get_refresh_token_key(self, user_id: str) -> str:
    """Generate Redis key for refresh token."""
    return f"{self.REFRESH_TOKEN_PREFIX}{user_id}"

  async def _decode_token(self, token: bytes) -> Optional[str]:
      """Safely decode token from bytes to string."""
      if not token:
        return None
      try:
        return token.decode("utf-8")
      except UnicodeDecodeError:
        raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="Failed to decode token"
        )
  async def store_refresh_token(self, user_id: str, refresh_token: str, ttl_days: int):
    key = await self._get_refresh_token_key(user_id)
    result =  await self.redis.setex(key,timedelta(days= ttl_days), value=refresh_token)
    if not result:
      raise HTTPException(status_codes = status.HTTP_500_INTERNAL_SERVER, details="An Error in the server")
    return result

  async def get_refresh_token(self, user_id: str) -> str:
    key = await self._get_refresh_token_key(user_id)
    stored_token = await self.redis.get(key)
    if not stored_token:
      raise HTTPException(status_codes = status.HTTP_404_NOT_FOUND, details= "Invalid or expired refresh token")
    return await self._decode_token(stored_token)

  async def delete_refresh_token(self, user_uid):
    key = await self._get_refresh_token_key(user_uid)
    result= await self.redis.delete(key)
    
    if result == 0:
      raise HTTPException(status_codes = status.HTTP_404_NOT_FOUND, details= "Invalid or expired refresh token")
    return True
  
  async def blacklist_refresh_token(self, rtuid: str):
    result = await self.redis.sadd(self.BLACKLIST_SET, rtuid)
    if not result:
      raise HTTPException(status_codes = status.HTTP_500_INTERNAL_SERVER, details= "An Error in the server")
    return 1
  
  async def is_token_blacklisted(self, rtuid: str):
    try:
      result = await self.redis.sismember(self.BLACKLIST_SET, rtuid)
      if result:
        raise HTTPException(status_codes=status.HTTP_401_UNAUTHORIZED, details="Refresh token is blacklisted")
      else:
        return 1
    except RedisError as rex:
      raise HTTPException(status_codes= status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(rex))


redis_config = {
  'host': setting.UPSTASH_REDIS_HOST,
  'port': setting.UPSTASH_REDIS_PORT,
  'password': setting.UPSTASH_REDIS_PASSWORD,
  'ssl': setting.UPSTASH_REDIS_SSL
}

# Initialize token manager
redis_manager = RedisManager(redis_config)


