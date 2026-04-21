import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2️⃣ leer variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 3️⃣ DEBUG (AHORA sí)
print("HOST:", DB_HOST)
print("PORT:", DB_PORT)
print("USER:", DB_USER)
print("PASSWORD:", DB_PASSWORD)
print("DB:", DB_NAME)

# 4️⃣ conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": True}
)
try:
    with engine.connect() as connection:
        print("✅ CONECTADO A LA BASE DE DATOS")
except Exception as e:
    print("❌ ERROR:", e)
