import aiosqlite
import os

# Allow overriding the DB path via environment variables (useful for Docker later)
DB_PATH = os.getenv("DATABASE_PATH", "flags.db")

async def init_db():
    """
    Initializes the SQLite database tables if they do not exist.
    This uses aiosqlite for non-blocking asynchronous database operations.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS flags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                enabled INTEGER NOT NULL DEFAULT 0,
                targeting_rule TEXT NOT NULL DEFAULT '{"type":"everyone"}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS configs (
                id TEXT PRIMARY KEY,
                description TEXT,
                value TEXT NOT NULL,
                value_type TEXT NOT NULL CHECK(value_type IN ('string','integer','float','boolean')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        await db.commit()

async def get_db():
    """
    FastAPI dependency that yields a database connection.
    Ensures the connection is closed after the request is completed.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Return rows as dictionaries instead of tuples for easier JSON serialization
        db.row_factory = aiosqlite.Row
        yield db