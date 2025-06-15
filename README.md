# Saloni Balkondekar Portfolio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Analytics](https://img.shields.io/badge/Analytics-Tracked-green.svg)](#analytics)

A comprehensive portfolio platform showcasing expertise in AI and Mechanical Engineering, featuring an interactive personal website and an AI-powered Text-to-CAD application with analytics tracking.

## Features

### Personal Portfolio Website
- **Interactive 3D Flower Animation**: Stunning animated flower with manual rotation controls
- **Responsive Design**: Optimized for all devices (desktop, tablet, mobile)
- **Modern UI**: Clean, professional design with smooth animations
- **Performance Optimized**: Lightweight, no external dependencies

### Text-to-CAD Application
- **AI-Powered 3D Generation**: Natural language to CAD model conversion
- **Professional 3D Viewport**: Three.js-based viewer with Blender-style controls
- **STL Export**: Production-ready files for 3D printing
- **Google OAuth Integration**: Secure authentication with usage limits
- **Live Code Editor**: Edit generated BadCAD code with real-time preview

### Analytics Platform
- **Real-time Tracking**: Page views, user sessions, CAD events
- **Admin Dashboard**: Comprehensive analytics and user management
- **Rate Limiting**: Abuse prevention and resource management
- **PostgreSQL Backend**: Persistent data storage with Docker support

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and start all services
git clone <repository-url>
cd saloni-balkondekar-portfolio
docker compose up --build

# Access the applications:
# Portfolio: http://localhost:8080
# Text-to-CAD: http://localhost:8081  
# Analytics Admin: http://localhost:8082/admin
# Backend API: http://localhost:8000
```

### Option 2: Individual Setup
```bash
# Start Analytics Service
cd analytics
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8082

# Start Text-to-CAD Backend
cd text-to-cad/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

# Serve Frontend Applications
cd saloni-balkondekar-website
python -m http.server 8080

cd text-to-cad/frontend
python -m http.server 8081
```

## Project Structure

```
saloni-balkondekar-portfolio/
├── README.md                     # Main project documentation
├── docker-compose.yml            # Full-stack orchestration
├── build.sh                      # Build automation script
├── check.sh                      # Health check script
├── docs/                         # Project documentation
│   ├── DEPLOYMENT_VM.md          # Deployment guide
│   └── docker-compose.minimal.yml
├── tests/                        # Integration tests
│   ├── test_all_fixes.py
│   ├── test_analytics_fixes.py
│   ├── test_backend_fixes.py
│   ├── test_database_connection.py
│   └── test_frontend_routes.py
├── nginx-proxy/                  # Reverse proxy configuration
│   ├── Dockerfile
│   ├── nginx.conf
│   └── text-to-cad-api-error.html
├── saloni-balkondekar-website/   # Personal portfolio website
│   ├── index.html               # Interactive 3D flower portfolio
│   ├── Dockerfile
│   └── src/                     # Stylesheets and scripts
│       ├── styles.css           # Main styles & design system
│       ├── flower.css           # 3D flower animations
│       ├── responsive.css       # Mobile-first responsive design
│       └── script.js            # Interactive functionality
├── text-to-cad/                 # AI-powered CAD application
│   ├── README.md                # Detailed Text-to-CAD docs
│   ├── docker-compose.yml       # Text-to-CAD specific setup
│   ├── backend/                 # Python FastAPI backend
│   │   ├── app.py              # Main API server
│   │   ├── requirements.txt    # Python dependencies
│   │   ├── core/               # Configuration and models
│   │   ├── api/                # API routes and dependencies
│   │   ├── services/           # Business logic services
│   │   ├── utils/              # Utility functions
│   │   └── tests/              # Comprehensive test suite
│   └── frontend/               # HTML/JS/CSS application
│       ├── index.html          # Main application interface
│       ├── components/         # Modular UI components
│       ├── scripts/            # Core application logic
│       └── styles/             # Component-specific styling
└── analytics/                   # Analytics and tracking service
    ├── app.py                  # FastAPI analytics server
    ├── requirements.txt        # Analytics dependencies
    ├── database.py             # PostgreSQL models
    ├── tracking.py             # Event tracking logic
    ├── auth.py                 # Session management
    ├── admin_dashboard.html    # Admin interface
    └── migration.py            # Database migrations
```

## Component Overview

### Personal Website (`saloni-balkondekar-website/`)
A modern, responsive portfolio featuring:
- **3D Animated Flower**: Interactive centerpiece with manual controls
- **Responsive Design**: Mobile-first approach with fluid layouts
- **Performance Optimized**: No dependencies, hardware-accelerated animations
- **Professional Styling**: Modern design system with CSS custom properties

### Text-to-CAD Application (`text-to-cad/`)
An AI-powered 3D modeling platform featuring:
- **BadCAD Integration**: Solid modeling engine for precise geometry
- **Three.js Viewport**: Interactive 3D visualization
- **AI Generation**: Natural language to CAD code conversion
- **Authentication**: Google OAuth with usage tracking
- **Modular Architecture**: Component-based frontend design

### Analytics Service (`analytics/`)
Comprehensive tracking and monitoring platform:
- **Real-time Analytics**: Page views, sessions, CAD events
- **User Management**: Authentication, limits, admin controls
- **Data Persistence**: PostgreSQL with Docker volumes
- **Rate Limiting**: IP and user-based abuse prevention

## Configuration

### Environment Variables
```bash
# Analytics Service
ADMIN_PASSWORD=your_secure_admin_password
SECRET_KEY=your_analytics_secret_key
DATABASE_URL=postgresql://user:pass@localhost:5432/analytics

# Text-to-CAD (Optional - for full AI functionality)
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
```

### Google OAuth Setup (Text-to-CAD)
For full AI functionality, follow the guide in [`text-to-cad/docs/GOOGLE_OAUTH_SETUP.md`](./text-to-cad/docs/GOOGLE_OAUTH_SETUP.md)

## Testing

Run the comprehensive test suite:
```bash
# Run all integration tests
python tests/test_all_fixes.py

# Test specific components
python tests/test_analytics_fixes.py
python tests/test_backend_fixes.py
python tests/test_database_connection.py
python tests/test_frontend_routes.py
```

## Deployment

### Production Deployment
1. **Set environment variables** in production environment
2. **Configure SSL certificates** for HTTPS
3. **Set up domain routing** to appropriate services
4. **Configure PostgreSQL** for analytics persistence

### Health Monitoring
```bash
# Check all services
./check.sh

# Individual service health
curl http://localhost:8082/health  # Analytics
curl http://localhost:8000/health  # Text-to-CAD API
```

## Analytics Dashboard

Access the admin dashboard at `http://localhost:8082/admin` to monitor:
- **Real-time Usage**: Page views, active sessions
- **User Analytics**: Registration, model generation counts
- **CAD Events**: Detailed generation tracking and performance
- **System Health**: Rate limiting, error logs

## Development

### Adding New Features
1. **Components**: Add to respective `components/` directories
2. **Styling**: Follow existing CSS architecture patterns
3. **Testing**: Add tests to `tests/` directory
4. **Documentation**: Update relevant README files

### Build System
```bash
# Build all services
./build.sh

# Individual builds
docker build -t portfolio-website ./saloni-balkondekar-website
docker build -t text-to-cad-backend ./text-to-cad/backend
docker build -t analytics-service ./analytics
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

- **Email**: saloni.balkondekar@gmail.com
- **LinkedIn**: [linkedin.com/in/salonibalkondekar](https://www.linkedin.com/in/salonibalkondekar)
- **GitHub**: [github.com/salonibalkondekar](https://github.com/salonibalkondekar)

---

Built with ❤️ by Saloni Balkondekar