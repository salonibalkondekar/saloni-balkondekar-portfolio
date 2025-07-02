# SSL/HTTPS Setup Guide for salonibalkondekar.codes

## Current Status

✅ **HTTP is working**: `http://salonibalkondekar.codes` is accessible  
❌ **HTTPS is not working**: SSL certificates need to be set up  
✅ **All services running**: Including the fixed news-gpt service  

## Issue Analysis

Your website is currently using the **development nginx configuration** which:
- Only supports HTTP (port 80)
- Doesn't have SSL/HTTPS configured
- Server name restricted to localhost only

The **production nginx configuration** has been prepared and includes:
- HTTPS/SSL support 
- HTTP-to-HTTPS redirects
- Proper domain name configuration
- Let's Encrypt certificate paths

## Solution: Two-Step SSL Setup

### Step 1: Prepare for SSL Certificate Generation

1. **Use the SSL preparation config** (allows certbot to work):
   ```bash
   cd /root/saloni-balkondekar-portfolio
   
   # Temporarily use the SSL prep config
   # Edit docker-compose.yml and change the CONFIG_FILE to:
   # CONFIG_FILE: nginx-ssl-prep.conf
   ```

2. **Rebuild and start containers**:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

3. **Verify HTTP access**:
   ```bash
   curl http://salonibalkondekar.codes
   # Should return 200 OK
   ```

### Step 2: Generate SSL Certificates

1. **Run the SSL setup script**:
   ```bash
   # Make sure you're on the server (not local machine)
   cd /root/saloni-balkondekar-portfolio
   sudo ./setup-ssl.sh
   ```

2. **The script will**:
   - Install certbot if needed
   - Create necessary directories  
   - Generate Let's Encrypt certificates for salonibalkondekar.codes
   - Set up auto-renewal via cron

3. **Follow the prompts** and ensure:
   - Your email is correct in the script
   - The domain is accessible via HTTP before running

### Step 3: Enable Full HTTPS Configuration

1. **Switch to production config**:
   ```bash
   # Edit docker-compose.yml and change back to:
   # CONFIG_FILE: nginx.conf
   ```

2. **Rebuild with SSL support**:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

3. **Test HTTPS**:
   ```bash
   curl https://salonibalkondekar.codes
   # Should return 200 OK with HTTPS
   ```

## Quick Commands for Remote Server

```bash
# 1. Pull latest changes
cd /root/saloni-balkondekar-portfolio
git pull origin main

# 2. Start with SSL prep config (edit docker-compose.yml first)
docker-compose down
docker-compose up --build -d

# 3. Generate SSL certificates
sudo ./setup-ssl.sh

# 4. Switch to full SSL config (edit docker-compose.yml again)
docker-compose down  
docker-compose up --build -d

# 5. Test both HTTP and HTTPS
curl http://salonibalkondekar.codes    # Should redirect to HTTPS
curl https://salonibalkondekar.codes   # Should work with SSL
```

## Troubleshooting

### If SSL certificate generation fails:
```bash
# Check if HTTP is accessible
curl -I http://salonibalkondekar.codes

# Check nginx logs
docker-compose logs proxy

# Verify domain DNS
nslookup salonibalkondekar.codes
```

### If HTTPS still doesn't work after setup:
```bash
# Check certificate files exist
sudo ls -la /etc/letsencrypt/live/salonibalkondekar.codes/

# Test certificate validity
sudo certbot certificates

# Check nginx configuration
docker-compose exec proxy nginx -t
```

### Certificate renewal testing:
```bash
# Test auto-renewal (dry run)
sudo certbot renew --dry-run
```

## Alternative: Quick HTTP-Only Fix

If you want to **temporarily fix the issue without SSL**:

1. **Edit docker-compose.yml**:
   ```yaml
   CONFIG_FILE: nginx-ssl-prep.conf  # Use the non-SSL config
   ```

2. **Remove the 443 port mapping**:
   ```yaml
   ports:
     - "80:80"    # Only HTTP
     # - "443:443"  # Comment out HTTPS
   ```

3. **Rebuild**:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

This will make your site fully accessible via HTTP while you work on SSL setup.

## Files Modified

- ✅ `nginx-proxy/nginx.conf` - Fixed syntax errors
- ✅ `docker-compose.yml` - Updated to use production config
- ✅ `nginx-proxy/nginx-ssl-prep.conf` - Temporary SSL prep config
- ✅ `setup-ssl.sh` - Automated SSL certificate setup script
- ✅ `news-gpt/Dockerfile` - Fixed Next.js standalone issue (already working)

## Next Steps

The recommended approach is to complete the SSL setup for a production-ready website. However, the HTTP-only option can be used as a quick fix if HTTPS is not immediately required.