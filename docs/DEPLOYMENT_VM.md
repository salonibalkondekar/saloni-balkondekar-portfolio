# Deployment Instructions for Resource-Constrained VM


## Option 1: Minimal Deployment (Recommended for 1GB RAM)

This excludes the analytics service to save resources:

```bash
# Make build script executable
chmod +x build.sh

# Use minimal docker-compose (no analytics/postgres)
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml build --no-cache
docker-compose -f docker-compose.minimal.yml up -d
```

## Option 2: Sequential Build (Full Deployment)

If you want all features including analytics:

```bash
# First, increase swap space on your VM
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Run sequential build
./build.sh
```

## Option 3: Pre-built Images (Fastest)

Build images locally and push to a registry:

```bash
# On your local machine:
docker-compose build
docker tag saloni-balkondekar-portfolio-backend your-registry/backend:latest
docker push your-registry/backend:latest
# Repeat for all services

# On VM:
# Update docker-compose.yml to use pre-built images
docker-compose pull
docker-compose up -d
```

## Monitoring Resources

```bash
# Watch memory usage during build
watch -n 1 free -h

# Check Docker resource usage
docker stats

# View build logs
docker-compose logs -f
```

## Troubleshooting

1. **Build timeout**: Use sequential build script
2. **Out of memory**: Add swap space or use minimal deployment
3. **Slow builds**: Consider upgrading VM to 2GB RAM

## Performance Tips

1. Build during low-traffic hours
2. Use Docker BuildKit for better caching:
   ```bash
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   ```
3. Prune unused Docker resources:
   ```bash
   docker system prune -a
   ```