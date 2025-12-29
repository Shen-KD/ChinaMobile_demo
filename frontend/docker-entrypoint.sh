#!/bin/sh
set -e

# Generate config.js from template using environment variables
envsubst '${VITE_SILICONFLOW_BASE_URL} ${VITE_SILICONFLOW_API_KEY} ${VITE_API_BASE_URL}' < /usr/share/nginx/html/config.js.template > /usr/share/nginx/html/config.js

# Generate nginx.conf from template
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start nginx
exec nginx -g "daemon off;"