import structlog
import sentry_sdk
from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import datetime

# sentry_sdk.init(dsn="your_sentry_dsn", traces_sample_rate=1.0)

structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(20))
logger = structlog.get_logger()

SECRET_KEY = "123456"  # 生产请用环境变量

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(401, "Invalid token")