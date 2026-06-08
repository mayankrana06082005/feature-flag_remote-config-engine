from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List, Any
from datetime import datetime

class TargetingRule(BaseModel):
    """
    Defines who is allowed to see a feature flag if it is enabled.
    Types: everyone, group, percentage, user_ids.
    """
    type: Literal["everyone", "group", "percentage", "user_ids"]
    groups: Optional[List[str]] = None
    percentage: Optional[int] = None
    ids: Optional[List[str]] = None

    @field_validator("percentage")
    @classmethod
    def validate_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("Percentage must be strictly between 0 and 100.")
        return v

class FlagCreate(BaseModel):
    id: str = Field(pattern=r'^[a-z0-9_]+$', description="Snake case ID, e.g., 'new_checkout'")
    name: str
    description: str = ""
    enabled: bool = False
    targeting_rule: TargetingRule = TargetingRule(type="everyone")

class FlagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    targeting_rule: Optional[TargetingRule] = None

class FlagResponse(FlagCreate):
    created_at: str
    updated_at: str

class ConfigCreate(BaseModel):
    id: str = Field(pattern=r'^[a-z0-9_]+$')
    description: str = ""
    value: str
    value_type: Literal['string', 'integer', 'float', 'boolean']

class ConfigUpdate(BaseModel):
    description: Optional[str] = None
    value: Optional[str] = None

class ConfigResponse(ConfigCreate):
    created_at: str
    updated_at: str