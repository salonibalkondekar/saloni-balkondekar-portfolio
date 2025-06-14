"""
Database models and connection for analytics service
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://analytics:analytics_password@postgres:5432/analytics_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable pooling for container environment
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class PageView(Base):
    """Track page views across all sites"""
    __tablename__ = "page_views"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    site = Column(String(50), index=True)  # 'portfolio' or 'text-to-cad'
    path = Column(String(500))
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    referrer = Column(Text)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True, nullable=True)
    
    # Performance index
    __table_args__ = (
        Index('idx_timestamp_site', 'timestamp', 'site'),
    )


class Session(Base):
    """User sessions for authentication"""
    __tablename__ = "sessions"
    
    id = Column(String(100), primary_key=True)  # UUID
    user_id = Column(String(100), index=True)
    email = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)


class User(Base):
    """User accounts with proper tracking"""
    __tablename__ = "users"
    
    id = Column(String(100), primary_key=True)  # Same as old system for compatibility
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    model_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)


class CADEvent(Base):
    """Detailed CAD generation events"""
    __tablename__ = "cad_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    event_type = Column(String(50))  # 'generate', 'execute', 'download', 'error'
    prompt = Column(Text, nullable=True)
    code = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    model_size_bytes = Column(Integer, nullable=True)
    ip_address = Column(String(45))


class RateLimit(Base):
    """Track rate limiting per IP/user"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    identifier = Column(String(100), unique=True, index=True)  # IP or user_id
    identifier_type = Column(String(20))  # 'ip' or 'user'
    request_count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    last_request = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)
    block_until = Column(DateTime, nullable=True)


class AdminLog(Base):
    """Log admin actions"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(45))
    success = Column(Boolean, default=True)


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()