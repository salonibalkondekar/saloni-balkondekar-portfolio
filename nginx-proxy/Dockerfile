FROM nginx:stable-alpine

RUN rm /etc/nginx/conf.d/default.conf

# Copy the appropriate config based on environment
# For development, use nginx-dev.conf
# For production, use nginx.conf (with SSL)
ARG CONFIG_FILE=nginx-dev.conf
COPY ${CONFIG_FILE} /etc/nginx/conf.d/nginx.conf
COPY error.html /usr/share/nginx/html/
