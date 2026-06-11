import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# System Role Access Credentials
INSPECTOR_USER = "smruti"
INSPECTOR_PASS = "smruti"

ADMIN_USER = "admin"
ADMIN_PASS = "admin"

def authenticate_inspector(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifies Field Revenue Inspector access logs."""
    is_user = secrets.compare_digest(credentials.username, INSPECTOR_USER)
    is_pass = secrets.compare_digest(credentials.password, INSPECTOR_PASS)
    if not (is_user and is_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Inspector Access.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def authenticate_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifies Registration Administrator portal access logs."""
    is_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_user and is_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Admin Access.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
