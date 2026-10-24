from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite connection configuration
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)

# Enable WAL mode and foreign key constraints for SQLite
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    """
    Lightweight schema migration to ensure backward compatibility on existing databases.
    """
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            if settings.database_url.startswith("sqlite"):
                res = conn.execute(text("PRAGMA table_info(payment_records)")).fetchall()
                cols = [c[1] for c in res]
                if cols and "approval_url" not in cols:
                    conn.execute(text("ALTER TABLE payment_records ADD COLUMN approval_url VARCHAR(512)"))
                    conn.commit()
    except Exception:
        pass
