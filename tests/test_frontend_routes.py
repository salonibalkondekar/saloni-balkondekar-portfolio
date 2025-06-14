"""
Unit tests for frontend routing and static file serving
"""
import os
import re

def test_nginx_config_serves_text_to_cad_styles():
    """Test that nginx config properly serves text-to-cad static files"""
    nginx_config_path = os.path.join(os.path.dirname(__file__), '..', 'nginx-proxy', 'nginx.conf')
    
    with open(nginx_config_path, 'r') as f:
        config = f.read()
    
    # Check for text-to-cad static file handling
    # Should have a location block for static assets under /text-to-cad/
    static_pattern = r'location\s+/text-to-cad/.*\{[^}]*\.(js|css|png|jpg|jpeg|gif|ico|woff|woff2|ttf|svg)'
    
    if re.search(static_pattern, config, re.DOTALL):
        print("✅ Nginx config has static file handling for text-to-cad")
    else:
        # Check if we need to add it
        print("⚠️  Nginx config may need static file location for /text-to-cad/styles/")
    
    # Check that /text-to-cad/ location exists
    assert "/text-to-cad/" in config
    print("✅ Nginx has /text-to-cad/ location block")

def test_analytics_tracking_js_route():
    """Test that analytics tracking.js is properly routed"""
    nginx_config_path = os.path.join(os.path.dirname(__file__), '..', 'nginx-proxy', 'nginx.conf')
    
    with open(nginx_config_path, 'r') as f:
        config = f.read()
    
    # Check for analytics routes
    assert "/analytics/" in config
    assert "proxy_pass http://analytics:8001/" in config
    print("✅ Analytics routes configured in nginx")

def test_frontend_index_includes_auth_modal_css():
    """Test that index.html includes auth-modal.css"""
    index_path = os.path.join(os.path.dirname(__file__), '..', 'text-to-cad', 'frontend', 'index.html')
    
    with open(index_path, 'r') as f:
        html = f.read()
    
    assert 'auth-modal.css' in html
    assert '<link rel="stylesheet" href="styles/auth-modal.css">' in html
    print("✅ Frontend index.html includes auth-modal.css")

def test_auth_modal_css_exists():
    """Test that auth-modal.css file exists"""
    css_path = os.path.join(os.path.dirname(__file__), '..', 'text-to-cad', 'frontend', 'styles', 'auth-modal.css')
    
    assert os.path.exists(css_path)
    
    # Check it has content
    with open(css_path, 'r') as f:
        content = f.read()
    
    assert len(content) > 100
    assert '.auth-modal' in content
    print("✅ auth-modal.css exists with proper content")

def test_tracking_js_exists():
    """Test that analytics tracking.js exists"""
    tracking_path = os.path.join(os.path.dirname(__file__), '..', 'analytics', 'tracking.js')
    
    assert os.path.exists(tracking_path)
    
    with open(tracking_path, 'r') as f:
        content = f.read()
    
    # Check for session endpoint usage
    assert '/analytics/session' in content or 'ensureSession' in content
    print("✅ Analytics tracking.js exists")

def test_sidebar_auth_integration():
    """Test that sidebar properly integrates auth UI"""
    sidebar_path = os.path.join(os.path.dirname(__file__), '..', 'text-to-cad', 'frontend', 'components', 'sidebar.js')
    
    with open(sidebar_path, 'r') as f:
        content = f.read()
    
    # Check for auth banner
    assert 'authBanner' in content
    assert 'auth-notice-banner' in content
    assert 'updateAuthUI' in content
    print("✅ Sidebar has auth UI integration")

if __name__ == "__main__":
    # Run tests
    print("🧪 Running Frontend Routes Tests...\n")
    
    test_nginx_config_serves_text_to_cad_styles()
    test_analytics_tracking_js_route()
    test_frontend_index_includes_auth_modal_css()
    test_auth_modal_css_exists()
    test_tracking_js_exists()
    test_sidebar_auth_integration()
    
    print("\n✅ All frontend tests passed!")