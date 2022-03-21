import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

HOST = str(os.getenv("HOST"))
DATABASE = str(os.getenv("DATABASE"))
USER = str(os.getenv("USER"))
PASSWORD = str(os.getenv("PASSWORD"))
PORT = str(os.getenv("PORT"))



