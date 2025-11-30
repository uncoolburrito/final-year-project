from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TriggerType(str, Enum):
    SPACE = "space"
    ENTER = "enter"
    NONE = "none"  # Expands immediately

class Snippet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    abbreviation: str
    expansion: str
    label: Optional[str] = None
    trigger: TriggerType = TriggerType.NONE
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self):
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    target_apps: List[str] = Field(default_factory=list) # List of executable names (e.g., "notepad.exe")
    snippets: List[Snippet] = Field(default_factory=list)
    is_active: bool = True

class Settings(BaseModel):
    engine_enabled: bool = True
    start_on_boot: bool = False
    dark_mode: bool = True
    accent_color: str = "blue"
    ignored_apps: List[str] = Field(default_factory=list) # Security: Apps to never expand in

class IPCMessage(BaseModel):
    type: str
    payload: dict = Field(default_factory=dict)
