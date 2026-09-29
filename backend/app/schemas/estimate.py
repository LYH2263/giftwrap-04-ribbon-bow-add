from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""
    bow_enabled: bool = False
    bow_m: float | None = None

class SettingsUpdate(BaseModel):
    bow_m: float | None = None
