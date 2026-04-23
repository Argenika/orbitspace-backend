import os
from sqlalchemy import create_engine

# 🔥 Leer variables de entorno (Render)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 🔥 Construir URL MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 🔥 Crear engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# 🔥 (Opcional) Test de conexión en arranque
try:
    with engine.connect() as connection:
        print("✅ Conectado a la base de datos")
except Exception as e:
    print("❌ Error conectando a la base de datos:", e)
