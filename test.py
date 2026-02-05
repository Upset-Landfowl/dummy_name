from app.core.config import get_settings
from app.core.settings import Settings
from dotenv import load_dotenv
js = get_settings()

print(get_settings().database_url)
print(type(get_settings().database_url))
#js = Settings
print(js.access_token_expire_minutes)
print(js.secret_key)
print(js.algorithm)
print(js.database_url)