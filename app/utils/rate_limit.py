
from fastapi import Request
from .jwt import decode_jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter_ip = Limiter(key_func=get_remote_address)

def per_user(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    
    if auth_header:
        try: 
            token = auth_header.split(" ")[1]
            user_id = decode_jwt(token).get("sub")
            return str(user_id)
        except Exception:
            pass

    if request.client:
        return request.client.host
    return "unknown"

limiter_user = Limiter(key_func=per_user)

