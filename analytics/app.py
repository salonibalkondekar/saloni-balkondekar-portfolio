"""
Analytics Service API
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session as DBSession
import time

from config import settings
from database import init_db, get_db, User, AdminLog
from auth import (
    SessionManager, RateLimiter, get_current_session, 
    require_session, check_admin_password, generate_csrf_token
)
from tracking import AnalyticsTracker
from migration import migrate_existing_data

# Create FastAPI app
app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and run migrations"""
    print("🚀 Initializing analytics database...")
    init_db()
    
    # Run migration if needed
    if os.path.exists("/app/collected_user_emails.json"):
        print("📦 Found existing user data, running migration...")
        migrate_existing_data("/app/collected_user_emails.json")
    
    print("✅ Analytics service ready!")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.service_name}


# Tracking endpoints
@app.post("/track/pageview")
async def track_pageview(
    request: Request,
    site: str,
    path: str,
    db: DBSession = Depends(get_db)
):
    """Track a page view"""
    # Check rate limit
    ip_address = request.client.host if request.client else "unknown"
    if not RateLimiter.check_rate_limit(db, ip_address):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get session info if available
    session = await get_current_session(request, db)
    session_id = session.id if session else None
    user_id = session.user_id if session else None
    
    # Track the view
    AnalyticsTracker.track_page_view(
        db, request, site, path, session_id, user_id
    )
    
    return {"success": True}


@app.post("/track/cad-event")
async def track_cad_event(
    request: Request,
    event_data: Dict[str, Any],
    session: Dict = Depends(require_session),
    db: DBSession = Depends(get_db)
):
    """Track CAD generation event"""
    start_time = time.time()
    
    # Extract IP
    ip_address = request.client.host if request.client else "unknown"
    
    # Track the event
    AnalyticsTracker.track_cad_event(
        db,
        user_id=session.user_id,
        session_id=session.id,
        event_type=event_data.get("event_type", "unknown"),
        ip_address=ip_address,
        prompt=event_data.get("prompt"),
        code=event_data.get("code"),
        success=event_data.get("success", True),
        error_message=event_data.get("error_message"),
        duration_ms=int((time.time() - start_time) * 1000),
        model_size_bytes=event_data.get("model_size_bytes")
    )
    
    return {"success": True}


# Session management endpoints
@app.post("/auth/create-session")
async def create_session(
    request: Request,
    response: Response,
    email: str = Form(...),
    name: str = Form(...),
    db: DBSession = Depends(get_db)
):
    """Create a new user session"""
    # Check rate limit
    ip_address = request.client.host if request.client else "unknown"
    if not RateLimiter.check_rate_limit(db, ip_address):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Generate user ID (same as old system for compatibility)
    import base64
    user_id = base64.b64encode(email.encode()).decode().replace("/", "").replace("+", "")[:20]
    
    # Get or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=user_id,
            email=email,
            name=name
        )
        db.add(user)
    else:
        # Update name if changed
        user.name = name
        user.last_activity = datetime.utcnow()
    
    # Check if user is blocked
    if user.is_blocked:
        raise HTTPException(
            status_code=403, 
            detail=f"Account blocked: {user.block_reason}"
        )
    
    db.commit()
    
    # Create session
    session_id = SessionManager.create_session(db, user_id, email, name, request)
    
    # Set secure cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax",
        max_age=settings.session_expire_hours * 3600
    )
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(session_id)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "model_count": user.model_count,
            "can_generate": user.model_count < 10  # Hardcoded limit for now
        },
        "csrf_token": csrf_token
    }


@app.post("/auth/destroy-session")
async def destroy_session(
    request: Request,
    response: Response,
    session: Dict = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """Destroy current session"""
    if session:
        SessionManager.destroy_session(db, session.id)
    
    # Clear cookie
    response.delete_cookie("session_id")
    
    return {"success": True}


@app.get("/auth/current-user")
async def get_current_user(
    session: Dict = Depends(require_session),
    db: DBSession = Depends(get_db)
):
    """Get current user info"""
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "model_count": user.model_count,
        "can_generate": user.model_count < 10
    }


# Admin endpoints
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard HTML"""
    # Read admin dashboard HTML (we'll create this next)
    with open("/app/admin_dashboard.html", "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@app.get("/tracking.js")
async def get_tracking_script():
    """Serve the tracking JavaScript"""
    return FileResponse("/app/tracking.js", media_type="application/javascript")


@app.post("/admin/login")
async def admin_login(
    request: Request,
    password: str = Form(...),
    db: DBSession = Depends(get_db)
):
    """Admin login"""
    ip_address = request.client.host if request.client else "unknown"
    
    # Check password
    if not check_admin_password(password):
        # Log failed attempt
        log = AdminLog(
            action="login_failed",
            details="Invalid password",
            ip_address=ip_address,
            success=False
        )
        db.add(log)
        db.commit()
        
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Log successful login
    log = AdminLog(
        action="login_success",
        details="Admin logged in",
        ip_address=ip_address,
        success=True
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "token": "admin_authenticated"}


@app.get("/admin/stats")
async def get_admin_stats(
    hours: int = 24,
    password: str = None,
    db: DBSession = Depends(get_db)
):
    """Get analytics statistics (requires admin password)"""
    if not password or not check_admin_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get various stats
    page_stats = AnalyticsTracker.get_page_view_stats(db, hours)
    cad_stats = AnalyticsTracker.get_cad_stats(db, hours)
    
    # Get user stats
    total_users = db.query(User).count()
    active_users_24h = db.query(User).filter(
        User.last_activity >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    return {
        "page_views": page_stats,
        "cad_events": cad_stats,
        "users": {
            "total": total_users,
            "active_24h": active_users_24h
        }
    }


@app.get("/admin/users")
async def get_admin_users(
    password: str = None,
    db: DBSession = Depends(get_db)
):
    """Get user list (requires admin password)"""
    if not password or not check_admin_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    users = db.query(User).order_by(User.last_activity.desc()).limit(100).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "model_count": user.model_count,
            "created_at": user.created_at.isoformat(),
            "last_activity": user.last_activity.isoformat(),
            "is_blocked": user.is_blocked
        }
        for user in users
    ]


@app.post("/admin/reset-user-count")
async def reset_user_count(
    user_id: str,
    password: str = None,
    db: DBSession = Depends(get_db)
):
    """Reset user's model count (admin only)"""
    if not password or not check_admin_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.model_count = 0
    db.commit()
    
    # Log action
    log = AdminLog(
        action="reset_user_count",
        details=f"Reset count for user {user.email}",
        ip_address="admin",
        success=True
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "new_count": 0}


# User management endpoints (for backend integration)
@app.post("/users/increment-count")
async def increment_user_count(
    user_id: str,
    session: Dict = Depends(require_session),
    db: DBSession = Depends(get_db)
):
    """Increment user's model count"""
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.model_count >= 10:
        raise HTTPException(status_code=403, detail="Model limit exceeded")
    
    user.model_count += 1
    user.last_activity = datetime.utcnow()
    db.commit()
    
    return {"success": True, "model_count": user.model_count}


@app.get("/users/{user_id}/info")
async def get_user_info(
    user_id: str,
    db: DBSession = Depends(get_db)
):
    """Get user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"model_count": 0}  # Return default for new users
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "model_count": user.model_count,
        "created_at": user.created_at.isoformat(),
        "can_generate": user.model_count < 10
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)