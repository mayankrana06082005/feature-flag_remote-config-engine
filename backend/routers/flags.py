from fastapi import APIRouter, Depends, HTTPException
from aiosqlite import Connection
import json
from datetime import datetime, timezone
from typing import List

from database import get_db
from models import FlagCreate, FlagUpdate, FlagResponse
from services.broadcaster import broadcaster

router = APIRouter(prefix="/flags", tags=["Flags"])

def format_flag_row(row: dict) -> dict:
    """Helper to convert a SQLite row into a dict compatible with FlagResponse."""
    d = dict(row)
    d["enabled"] = bool(d["enabled"])
    # Targeting rule is stored as a JSON string in DB; parse it back to a dict
    d["targeting_rule"] = json.loads(d["targeting_rule"])
    return d

@router.get("", response_model=List[FlagResponse])
async def list_flags(db: Connection = Depends(get_db)):
    """Retrieve all feature flags."""
    async with db.execute("SELECT * FROM flags") as cursor:
        rows = await cursor.fetchall()
        return [format_flag_row(row) for row in rows]

@router.get("/{flag_id}", response_model=FlagResponse)
async def get_flag(flag_id: str, db: Connection = Depends(get_db)):
    """Retrieve a single feature flag by ID."""
    async with db.execute("SELECT * FROM flags WHERE id = ?", (flag_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Flag not found")
        return format_flag_row(row)

@router.post("", response_model=FlagResponse)
async def create_flag(flag: FlagCreate, db: Connection = Depends(get_db)):
    """Create a new feature flag."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        await db.execute(
            """
            INSERT INTO flags (id, name, description, enabled, targeting_rule, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                flag.id,
                flag.name,
                flag.description,
                int(flag.enabled),
                flag.targeting_rule.model_dump_json(),
                now,
                now
            )
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating flag. ID might already exist. Details: {e}")

    # Fetch and broadcast the created flag
    async with db.execute("SELECT * FROM flags WHERE id = ?", (flag.id,)) as cursor:
        row = await cursor.fetchone()
        flag_data = format_flag_row(row)
        await broadcaster.broadcast("flag_updated", flag_data)
        return flag_data

@router.patch("/{flag_id}", response_model=FlagResponse)
async def update_flag(flag_id: str, flag_update: FlagUpdate, db: Connection = Depends(get_db)):
    """Update specific fields of an existing feature flag."""
    async with db.execute("SELECT * FROM flags WHERE id = ?", (flag_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Flag not found")
    
    current_data = dict(row)
    updates = flag_update.model_dump(exclude_unset=True)
    
    if not updates:
        return format_flag_row(current_data)

    now = datetime.now(timezone.utc).isoformat()
    set_clauses = []
    values = []

    # Dynamically build the SQL UPDATE statement
    for key, value in updates.items():
        set_clauses.append(f"{key} = ?")
        if key == "targeting_rule":
            values.append(flag_update.targeting_rule.model_dump_json())
        elif key == "enabled":
            values.append(int(value))
        else:
            values.append(value)
            
    set_clauses.append("updated_at = ?")
    values.append(now)
    values.append(flag_id)

    query = f"UPDATE flags SET {', '.join(set_clauses)} WHERE id = ?"
    await db.execute(query, values)
    await db.commit()

    # Fetch updated flag and broadcast
    async with db.execute("SELECT * FROM flags WHERE id = ?", (flag_id,)) as cursor:
        updated_row = await cursor.fetchone()
        flag_data = format_flag_row(updated_row)
        await broadcaster.broadcast("flag_updated", flag_data)
        return flag_data

@router.delete("/{flag_id}")
async def delete_flag(flag_id: str, db: Connection = Depends(get_db)):
    """Delete a feature flag completely."""
    await db.execute("DELETE FROM flags WHERE id = ?", (flag_id,))
    await db.commit()
    await broadcaster.broadcast("flag_deleted", {"id": flag_id})
    return {"message": "Flag deleted successfully"}