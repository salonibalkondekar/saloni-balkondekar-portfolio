#!/bin/bash
# SSL Certificate Setup Script for salonibalkondekar.codes
set -e

echo "🔐 Setting up SSL certificates for salonibalkondekar.codes..."

DOMAIN="salonibalkondekar.codes"
EMAIL="your-email@example.com"  # Replace with your actual email

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt update
    apt install -y certbot
fi

# Create webroot directory
echo "📁 Creating webroot directory..."
mkdir -p /var/www/certbot

# Check if certificates already exist
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "✅ SSL certificates already exist for $DOMAIN"
    echo "📋 Certificate info:"
    certbot certificates -d $DOMAIN
else
    echo "🆕 Obtaining new SSL certificate for $DOMAIN..."
    
    # First, let's make sure the nginx is running HTTP-only to get the certificate
    echo "⚠️  Make sure your nginx is running and accessible via HTTP before proceeding"
    echo "   Run: docker-compose up proxy"
    echo "   Test: curl http://$DOMAIN"
    read -p "Press Enter when ready to continue..."
    
    # Get certificate using webroot method
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    if [ $? -eq 0 ]; then
        echo "✅ SSL certificates obtained successfully!"
    else
        echo "❌ Failed to obtain SSL certificates"
        exit 1
    fi
fi

# Set up auto-renewal
echo "🔄 Setting up automatic renewal..."
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    echo "✅ Auto-renewal cron job added"
else
    echo "✅ Auto-renewal already configured"
fi

# Show certificate status
echo "📋 Certificate status:"
certbot certificates

echo ""
echo "🎉 SSL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the EMAIL variable in this script with your actual email"
echo "2. Restart your containers: docker-compose down && docker-compose up --build -d"
echo "3. Test HTTPS: curl https://$DOMAIN"
echo ""
echo "💡 The certificates will auto-renew via cron job"
echo "   To test renewal: certbot renew --dry-run"