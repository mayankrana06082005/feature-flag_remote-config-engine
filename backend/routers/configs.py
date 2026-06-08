from fastapi import APIRouter, Depends, HTTPException
from aiosqlite import Connection
from datetime import datetime, timezone
from typing import List

from database import get_db
from models import ConfigCreate, ConfigUpdate, ConfigResponse
from services.broadcaster import broadcaster

router = APIRouter(prefix="/configs", tags=["Configs"])

def format_config_row(row: dict) -> dict:
    """Helper to convert a SQLite row into a dict compatible with ConfigResponse."""
    return dict(row)

@router.get("", response_model=List[ConfigResponse])
async def list_configs(db: Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM configs") as cursor:
        rows = await cursor.fetchall()
        return [format_config_row(row) for row in rows]

@router.post("", response_model=ConfigResponse)
async def create_config(config: ConfigCreate, db: Connection = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    try:
        await db.execute(
            """
            INSERT INTO configs (id, description, value, value_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (config.id, config.description, config.value, config.value_type, now, now)
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating config. Details: {e}")

    async with db.execute("SELECT * FROM configs WHERE id = ?", (config.id,)) as cursor:
        row = await cursor.fetchone()
        config_data = format_config_row(row)
        await broadcaster.broadcast("config_updated", config_data)
        return config_data

@router.patch("/{config_id}", response_model=ConfigResponse)
async def update_config(config_id: str, config_update: ConfigUpdate, db: Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM configs WHERE id = ?", (config_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Config not found")
    
    updates = config_update.model_dump(exclude_unset=True)
    if not updates:
        return format_config_row(dict(row))

    now = datetime.now(timezone.utc).isoformat()
    set_clauses = []
    values = []

    for key, value in updates.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
            
    set_clauses.append("updated_at = ?")
    values.append(now)
    values.append(config_id)

    query = f"UPDATE configs SET {', '.join(set_clauses)} WHERE id = ?"
    await db.execute(query, values)
    await db.commit()

    async with db.execute("SELECT * FROM configs WHERE id = ?", (config_id,)) as cursor:
        updated_row = await cursor.fetchone()
        config_data = format_config_row(updated_row)
        await broadcaster.broadcast("config_updated", config_data)
        return config_data