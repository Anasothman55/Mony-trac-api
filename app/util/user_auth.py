from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from ..core.config import setting
from fastapi import HTTPException, status


pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

serializer = URLSafeTimedSerializer(
  secret_key=setting.SECRET_KEY,
  salt="email-config"
)

class  UserAuthUtils:

  @staticmethod
  def hash_password_utils(password: str) -> str:
    return pwd.hash(password)
  @staticmethod
  def verify_password_utils(plain_password: str, hash_password: str) -> bool:
    return pwd.verify(plain_password, hash_password)

  @staticmethod
  def error_schema(body: str, field: str):
    return {
      "type": "UniqueViolation",
      "loc": [ body],
      "msg": f"{body} already exists",
      "input": field
    }

  @staticmethod
  def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token
  @staticmethod
  def decode_url_safe_token(token: str):
    try:
      token_data = serializer.loads(token)
      return token_data
    except Exception as e:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid token"})




