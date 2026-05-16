# backend/api/routes/devices.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.device_service import DeviceService
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep
from models.schemas.outcome import DeviceOut

router = APIRouter()


@router.get("/", response_model=List[DeviceOut],
            summary="List all devices linked to the current rep")
def list_devices(
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    return DeviceService(db).list_for_rep(current.id)


@router.delete("/{device_id}", response_model=DeviceOut,
               summary="Revoke a device (it can no longer sync outcomes)")
def revoke_device(
    device_id: str,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    return DeviceService(db).revoke(device_id, current.id)