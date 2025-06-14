# Analytics Service

This service provides:
- **Page view tracking** for both portfolio and text-to-cad sites
- **Session-based authentication** with secure cookies
- **User management** with model generation limits
- **Detailed CAD event tracking**
- **Admin dashboard** for monitoring usage
- **Rate limiting** to prevent abuse

## Features

### 1. Tracking
- Automatic page view tracking via JavaScript snippet
- CAD generation event tracking (prompts, success/failure, timing)
- User session tracking with cookies
- IP-based and user-based rate limiting

### 2. Authentication
- Session-based auth (no more email prompts!)
- Secure httpOnly cookies
- CSRF protection
- Automatic session expiry (7 days)

### 3. Admin Dashboard
Access at: `https://salonibalkondekar.codes/admin`
- Real-time analytics
- User management
- Reset user counts
- View generation history

### 4. Data Persistence
- PostgreSQL database
- Docker volumes for data persistence
- Automatic migration of existing user data

## Environment Variables

```bash
# Required
ADMIN_PASSWORD=your_secure_password

# Optional (have defaults)
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:pass@host:5432/db
```

## API Endpoints

### Public
- `GET /health` - Health check
- `GET /tracking.js` - JavaScript tracking snippet
- `POST /track/pageview` - Track page views
- `POST /auth/create-session` - Create user session
- `GET /admin` - Admin dashboard (password protected)

### Authenticated (require session)
- `POST /track/cad-event` - Track CAD events
- `POST /users/increment-count` - Increment model count
- `GET /auth/current-user` - Get current user info

### Admin (require password)
- `POST /admin/login` - Admin login
- `GET /admin/stats` - Get analytics stats
- `GET /admin/users` - List users
- `POST /admin/reset-user-count` - Reset user's count

## Database Schema

- `page_views` - All page view events
- `sessions` - User sessions
- `users` - User accounts and limits
- `cad_events` - Detailed CAD generation tracking
- `rate_limits` - Rate limiting data
- `admin_logs` - Admin action audit trail