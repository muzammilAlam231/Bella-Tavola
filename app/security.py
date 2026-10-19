import secrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import settings
basic = HTTPBasic(auto_error=False)
def require_admin(credentials: HTTPBasicCredentials | None = Depends(basic)) -> str:
    if credentials is not None:
        # compare_digest takes constant time, which prevents timing attacks
        user_ok = secrets.compare_digest(credentials.username.encode(), settings.admin_username.encode())
        pass_ok = secrets.compare_digest(credentials.password.encode(), settings.admin_password.encode())
        if user_ok and pass_ok:
            return credentials.username
    # Deliberately NO "WWW-Authenticate" header: it would trigger the browser's ugly login popup
    raise HTTPException(status_code=401, detail="Invalid or missing admin credentials")