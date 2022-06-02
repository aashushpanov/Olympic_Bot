import os
from dotenv import load_dotenv


# load_dotenv()
env_vars = os.environ.copy()


BOT_TOKEN = str(env_vars.get("BOT_TOKEN"))

HOST = str(env_vars.get("HOST"))
DATABASE = str(env_vars.get("DATABASE"))
USER = str(env_vars.get("USER"))
PASSWORD = str(env_vars.get("PASSWORD"))
PORT = str(env_vars.get("PORT"))
URL = str(env_vars.get("URL_VPS"))

ADMIN_GROUP_ID = str(env_vars.get("ADMIN_GROUP_ID"))
CLASS_MANAGERS_PASSWORD = str(env_vars.get("CLASS_MANAGERS_PASSWORD"))

GOOGLE_WEB_CLIENT = str(env_vars.get("GOOGLE_WEB_CLIENT"))
GOOGLE_SERVICE_ACCOUNT = str(env_vars.get("GOOGLE_SERVICE_ACCOUNT"))


