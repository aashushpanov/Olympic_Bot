import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN2"))

HOST = str(os.getenv("HOST"))
DATABASE = str(os.getenv("DATABASE"))
USER = str(os.getenv("USER"))
PASSWORD = str(os.getenv("PASSWORD"))
PORT = str(os.getenv("PORT"))
URL = str(os.getenv("URL_VPS"))

ADMIN_GROUP_ID = str(os.getenv("ADMIN_GROUP_ID"))
CLASS_MANAGERS_GROUP_ID = str(os.getenv("CLASS_MANAGERS_GROUP_ID"))


