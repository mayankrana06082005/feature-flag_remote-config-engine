from fastapi import APIRouter, Depends
from pydantic import BaseModel
from aiosqlite import Connection
import json
from typing import List, Dict, Any

from database import get_db
from services.targeting import evaluate_flag

router = APIRouter(tags=["Evaluation"])

class EvaluationContext(BaseModel):
    userId: str
    groups: List[str] = []

@router.post("/evaluate")
async def evaluate_all(context: EvaluationContext, db: Connection = Depends(get_db)):
    """
    Evaluates all flags against the provided user context and returns 
    a consolidated dictionary of active flags and configurations.
    """
    user_context_dict = context.model_dump()
    
    evaluated_flags: Dict[str, bool] = {}
    async with db.execute("SELECT id, enabled, targeting_rule FROM flags") as cursor:
        flags = await cursor.fetchall()
        for row in flags:
            flag_dict = dict(row)
            flag_dict["enabled"] = bool(flag_dict["enabled"])
            flag_dict["targeting_rule"] = json.loads(flag_dict["targeting_rule"])
            
            is_enabled = evaluate_flag(flag_dict, user_context_dict)
            evaluated_flags[flag_dict["id"]] = is_enabled

    evaluated_configs: Dict[str, Any] = {}
    async with db.execute("SELECT id, value, value_type FROM configs") as cursor:
        configs = await cursor.fetchall()
        for row in configs:
            val = row["value"]
            v_type = row["value_type"]
            if v_type == 'integer':
                val = int(val)
            elif v_type == 'float':
                val = float(val)
            elif v_type == 'boolean':
                val = str(val).lower() in ('true', '1', 'yes')
            
            evaluated_configs[row["id"]] = val

    return {
        "flags": evaluated_flags,
        "configs": evaluated_configs
    }