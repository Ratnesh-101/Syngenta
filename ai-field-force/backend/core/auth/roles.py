# backend/core/auth/roles.py
"""
Role-based access control. Use as a FastAPI dependency:

    @router.post("/something", dependencies=[Depends(require_role("manager", "admin"))])
    def manager_only_endpoint(...):
        ...

Or:

    @router.post("/something")
    def manager_only_endpoint(current: Rep = Depends(require_role("manager", "admin"))):
        ...

Roles in this system: "rep" | "manager" | "admin".
"""
from fastapi import Depends, HTTPException, status
from models.db.rep import Rep
from core.auth.dependencies import get_current_rep


def require_role(*allowed_roles: str):
    def _checker(current: Rep = Depends(get_current_rep)) -> Rep:
        if current.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires one of: {', '.join(allowed_roles)}. "
                       f"Your role: {current.role}.",
            )
        return current
    return _checker