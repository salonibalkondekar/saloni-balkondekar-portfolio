/**
 * Analytics tracking script
 * Include this in all pages to track page views
 */
(function() {
    // Determine site based on URL
    const site = window.location.pathname.startsWith('/text-to-cad') ? 'text-to-cad' : 'portfolio';
    
    // Create session if needed
    async function ensureSession() {
        try {
            const response = await fetch('/analytics/session', {
                method: 'POST',
                credentials: 'include'
            });
            return response.ok;
        } catch (err) {
            console.error('Session creation error:', err);
            return false;
        }
    }
    
    // Track page view
    async function trackPageView() {
        // Ensure session exists first
        await ensureSession();
        
        fetch('/analytics/track/pageview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                site: site,
                path: window.location.pathname
            })
        }).catch(err => console.error('Analytics error:', err));
    }
    
    // Track on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trackPageView);
    } else {
        trackPageView();
    }
    
    // Track on route change (for SPAs)
    let lastPath = window.location.pathname;
    setInterval(() => {
        if (window.location.pathname !== lastPath) {
            lastPath = window.location.pathname;
            trackPageView();
        }
    }, 1000);
})();