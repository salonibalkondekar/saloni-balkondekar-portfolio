# Analytics Integration Tests

This directory contains comprehensive tests for the analytics integration system.

## Test Files

### Core Integration Tests
- **`simple_test.py`** - Quick integration test for basic analytics functionality
- **`test_analytics_integration.py`** - Comprehensive test suite for all analytics features

### Existing Tests
- **`test_all_fixes.py`** - General fix validation
- **`test_analytics_fixes.py`** - Analytics-specific fixes
- **`test_backend_fixes.py`** - Backend fix validation
- **`test_database_connection.py`** - Database connectivity tests
- **`test_frontend_routes.py`** - Frontend routing tests

## Running Tests

### Quick Integration Test
```bash
# From project root
python tests/simple_test.py

# Or from tests directory
cd tests && python simple_test.py
```

### Comprehensive Test Suite
```bash
# From project root
python tests/test_analytics_integration.py

# Or from tests directory
cd tests && python test_analytics_integration.py
```

## Prerequisites

1. **Services Running**: 

   **For Local Development:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d
   ```
   This exposes services on:
   - Analytics: http://localhost:8001
   - Backend: http://localhost:8000  
   - Frontend: http://localhost:5173
   - Portfolio: http://localhost:4000

   **For Production (VM):**
   ```bash
   docker-compose up -d
   ```

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install requests pytest
   ```

## Test Features

### Analytics Integration Tests Cover:
- ✅ Analytics service health checks
- ✅ User session creation and management
- ✅ Page view tracking
- ✅ Portfolio link click tracking  
- ✅ Portfolio scroll milestone tracking
- ✅ Model generation with comprehensive data collection
- ✅ User count incrementation and limits
- ✅ Session persistence across requests
- ✅ Rate limiting functionality
- ✅ Database data verification

### Expected Results:
- All services healthy and responsive
- User sessions created successfully with analytics backend
- Model counters update correctly (0/10 → 1/10 → etc.)
- Comprehensive data collection for user prompts, generated code, and STL files
- Portfolio engagement tracking (link clicks, scroll behavior)
- Usage limits properly enforced at 10 models per user

## Troubleshooting

If tests fail:

1. **Check Service Status**:
   ```bash
   docker-compose ps
   ```

2. **Check Service Logs**:
   ```bash
   docker-compose logs analytics
   docker-compose logs backend
   ```

3. **Verify Database Schema**:
   ```bash
   docker exec -it $(docker ps -q -f name=postgres) psql -U analytics -d analytics_db -c "\d cad_events"
   ```

4. **Test Direct Service Access**:
   ```bash
   docker exec $(docker ps -q -f name=analytics) curl -s http://localhost:8001/health
   ```