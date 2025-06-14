"""
Analytics tracking functions
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, and_
from fastapi import Request

from database import PageView, CADEvent, User, Session


class AnalyticsTracker:
    """Track analytics events"""
    
    @staticmethod
    def track_page_view(
        db: DBSession,
        request: Request,
        site: str,
        path: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Track a page view"""
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", "")
        
        page_view = PageView(
            site=site,
            path=path,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id,
            user_id=user_id
        )
        db.add(page_view)
        db.commit()
    
    @staticmethod
    def track_cad_event(
        db: DBSession,
        user_id: str,
        session_id: str,
        event_type: str,
        ip_address: str,
        prompt: Optional[str] = None,
        code: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        model_size_bytes: Optional[int] = None
    ) -> None:
        """Track CAD generation event"""
        event = CADEvent(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            prompt=prompt,
            code=code,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            model_size_bytes=model_size_bytes,
            ip_address=ip_address
        )
        db.add(event)
        db.commit()
    
    @staticmethod
    def get_page_view_stats(
        db: DBSession,
        hours: int = 24,
        site: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get page view statistics"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(PageView).filter(PageView.timestamp >= since)
        if site:
            query = query.filter(PageView.site == site)
        
        total_views = query.count()
        unique_visitors = db.query(func.count(func.distinct(PageView.ip_address))).filter(
            PageView.timestamp >= since
        ).scalar()
        
        # Views by site
        views_by_site = db.query(
            PageView.site,
            func.count(PageView.id).label('count')
        ).filter(
            PageView.timestamp >= since
        ).group_by(PageView.site).all()
        
        # Top pages
        top_pages = db.query(
            PageView.path,
            func.count(PageView.id).label('count')
        ).filter(
            PageView.timestamp >= since
        ).group_by(PageView.path).order_by(func.count(PageView.id).desc()).limit(10).all()
        
        return {
            "total_views": total_views,
            "unique_visitors": unique_visitors,
            "views_by_site": {site: count for site, count in views_by_site},
            "top_pages": [{"path": path, "views": count} for path, count in top_pages]
        }
    
    @staticmethod
    def get_cad_stats(
        db: DBSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get CAD generation statistics"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Total events
        total_events = db.query(CADEvent).filter(
            CADEvent.timestamp >= since
        ).count()
        
        # Events by type
        events_by_type = db.query(
            CADEvent.event_type,
            func.count(CADEvent.id).label('count')
        ).filter(
            CADEvent.timestamp >= since
        ).group_by(CADEvent.event_type).all()
        
        # Success rate
        success_count = db.query(CADEvent).filter(
            and_(
                CADEvent.timestamp >= since,
                CADEvent.success == True
            )
        ).count()
        
        success_rate = (success_count / total_events * 100) if total_events > 0 else 0
        
        # Active users
        active_users = db.query(
            func.count(func.distinct(CADEvent.user_id))
        ).filter(
            CADEvent.timestamp >= since
        ).scalar()
        
        # Average generation time
        avg_duration = db.query(
            func.avg(CADEvent.duration_ms)
        ).filter(
            and_(
                CADEvent.timestamp >= since,
                CADEvent.duration_ms.isnot(None)
            )
        ).scalar()
        
        return {
            "total_events": total_events,
            "events_by_type": {event_type: count for event_type, count in events_by_type},
            "success_rate": round(success_rate, 2),
            "active_users": active_users,
            "avg_duration_ms": int(avg_duration) if avg_duration else 0
        }
    
    @staticmethod
    def get_user_activity(
        db: DBSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Get activity for specific user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Recent events
        recent_events = db.query(CADEvent).filter(
            CADEvent.user_id == user_id
        ).order_by(CADEvent.timestamp.desc()).limit(10).all()
        
        # Total generations
        total_generations = db.query(CADEvent).filter(
            and_(
                CADEvent.user_id == user_id,
                CADEvent.event_type == "generate"
            )
        ).count()
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "model_count": user.model_count,
                "is_blocked": user.is_blocked
            },
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "prompt": event.prompt[:100] if event.prompt else None,
                    "success": event.success
                }
                for event in recent_events
            ],
            "total_generations": total_generations
        }