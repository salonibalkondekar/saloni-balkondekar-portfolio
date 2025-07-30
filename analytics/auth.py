"""
Authentication and session management
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession
from passlib.context import CryptContext
import base64

from database import get_db, Session, User, RateLimit
from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SessionManager:
    """Manage user sessions with secure cookies"""

    @staticmethod
    def create_session(
        db: DBSession, user_id: str, email: str, name: str, request: Request
    ) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())

        # Get client info
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Create session in database
        db_session = Session(
            id=session_id,
            user_id=user_id,
            email=email,
            name=name,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow()
            + timedelta(hours=settings.session_expire_hours),
        )
        db.add(db_session)
        db.commit()

        return session_id

    @staticmethod
    def get_session(db: DBSession, session_id: str) -> Optional[Session]:
        """Get and validate session"""
        if not session_id:
            return None

        session = (
            db.query(Session)
            .filter(
                Session.id == session_id,
                Session.is_active == True,
                Session.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if session:
            # Update last seen
            session.last_seen = datetime.utcnow()
            db.commit()

        return session

    @staticmethod
    def destroy_session(db: DBSession, session_id: str) -> None:
        """Destroy a session"""
        session = db.query(Session).filter(Session.id == session_id).first()
        if session:
            session.is_active = False
            db.commit()


class RateLimiter:
    """Rate limiting to prevent abuse"""

    @staticmethod
    def check_rate_limit(
        db: DBSession, identifier: str, identifier_type: str = "ip"
    ) -> bool:
        """Check if identifier is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=settings.rate_limit_window_minutes)

        # Get or create rate limit record
        rate_limit = (
            db.query(RateLimit)
            .filter(
                RateLimit.identifier == identifier,
                RateLimit.identifier_type == identifier_type,
            )
            .first()
        )

        if not rate_limit:
            rate_limit = RateLimit(
                identifier=identifier,
                identifier_type=identifier_type,
                request_count=0,
                window_start=now,
            )
            db.add(rate_limit)

        # Check if blocked
        if rate_limit.is_blocked and rate_limit.block_until > now:
            return False

        # Reset window if needed
        if rate_limit.window_start < window_start:
            rate_limit.window_start = now
            rate_limit.request_count = 0
            rate_limit.is_blocked = False

        # Increment counter
        rate_limit.request_count += 1
        rate_limit.last_request = now

        # Check limit
        if rate_limit.request_count > settings.rate_limit_requests:
            rate_limit.is_blocked = True
            rate_limit.block_until = now + timedelta(
                minutes=settings.rate_limit_block_minutes
            )
            db.commit()
            return False

        db.commit()
        return True


async def get_current_session(
    request: Request, db: DBSession = Depends(get_db)
) -> Optional[Session]:
    """Get current session from cookie"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    return SessionManager.get_session(db, session_id)


async def require_session(
    session: Optional[Session] = Depends(get_current_session),
) -> Session:
    """Require valid session"""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session


def check_admin_password(password: str) -> bool:
    """Verify admin password"""
    return password == settings.admin_password


def verify_csrf_token(request: Request, token: str) -> bool:
    """Verify CSRF token"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return False

    # Simple CSRF: hash of session_id + secret
    import hashlib

    expected = hashlib.sha256(
        f"{session_id}{settings.secret_key}".encode()
    ).hexdigest()[:32]

    return secrets.compare_digest(token, expected)


def generate_csrf_token(session_id: str) -> str:
    """Generate CSRF token for session"""
    import hashlib

    return hashlib.sha256(f"{session_id}{settings.secret_key}".encode()).hexdigest()[
        :32
    ]
