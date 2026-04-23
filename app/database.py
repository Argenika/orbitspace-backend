from sqlalchemy import create_engine
import os

# 🔥 Render ya te da esta variable automáticamente
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 conexión a la base de datos (PostgreSQL)
engine = create_engine(DATABASE_URL)
