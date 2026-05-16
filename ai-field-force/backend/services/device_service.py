# backend/services/device_service.py
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.db.device import Device


class DeviceService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_device(
        self,
        *,
        device_id: str,
        rep_id: str,
        name: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> Device:
        """Get-or-create. Updates last_seen_at. Rejects cross-rep takeover attempts."""
        device = self.db.query(Device).filter(Device.id == device_id).first()
        now = datetime.utcnow()

        if device:
            # Security: a device that's already linked to a different rep
            # cannot be silently rebound. This stops a stolen device_id from
            # leaking outcomes between accounts.
            if device.rep_id != rep_id:
                raise HTTPException(
                    status_code=409,
                    detail="This device_id is already linked to a different account",
                )
            if device.is_revoked:
                raise HTTPException(
                    status_code=403,
                    detail="This device has been revoked. Please re-register.",
                )
            device.last_seen_at = now
            if name and not device.name:
                device.name = name
            if platform and not device.platform:
                device.platform = platform
        else:
            device = Device(
                id=device_id,
                rep_id=rep_id,
                name=name,
                platform=platform,
                first_seen_at=now,
                last_seen_at=now,
                sync_count="0",
            )
            self.db.add(device)

        self.db.commit()
        self.db.refresh(device)
        return device

    def mark_sync(self, device: Device, n: int) -> None:
        """Bump sync stats after a successful batch."""
        device.last_sync_at = datetime.utcnow()
        device.last_seen_at = datetime.utcnow()
        try:
            current = int(device.sync_count or "0")
        except (TypeError, ValueError):
            current = 0
        device.sync_count = str(current + n)
        self.db.commit()

    def list_for_rep(self, rep_id: str) -> List[Device]:
        return (
            self.db.query(Device)
            .filter(Device.rep_id == rep_id)
            .order_by(Device.last_seen_at.desc())
            .all()
        )

    def revoke(self, device_id: str, rep_id: str) -> Device:
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        if device.rep_id != rep_id:
            raise HTTPException(status_code=403, detail="Not your device")
        device.is_revoked = True
        self.db.commit()
        self.db.refresh(device)
        return device