from fastapi import APIRouter, HTTPException
from app.repositories import settings_repo
from app.schemas.estimate import SettingsUpdate
router = APIRouter()
@router.get("/settings")
def settings(): return settings_repo.get_all()
@router.put("/settings")
def update_settings(body: SettingsUpdate):
    if body.bow_m is not None:
        if float(body.bow_m) <= 0:
            raise HTTPException(400, "bow_m must be positive")
        settings_repo.set_value("bow_m", str(float(body.bow_m)))
    return settings_repo.get_all()
