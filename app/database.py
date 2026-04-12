from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Cambia estos datos si tu MySQL es diferente
DATABASE_URL = "mysql+pymysql://root:password@localhost/ospace2"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
