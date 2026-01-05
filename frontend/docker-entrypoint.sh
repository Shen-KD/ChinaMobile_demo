#!/bin/sh
set -e

# Set default AVAILABLE_MODELS if not provided
if [ -z "$AVAILABLE_MODELS" ]; then
  export AVAILABLE_MODELS='[ { "id": "DeepSeek-V3.1", "name": "DeepSeek-V3", "description": "通用对话模型，性能均衡", "provider": "DeepSeek" } ]'
fi

# Generate config.js from template using environment variables
envsubst '${VITE_SILICONFLOW_BASE_URL} ${VITE_SILICONFLOW_API_KEY} ${VITE_API_BASE_URL} ${AVAILABLE_MODELS}' < /usr/share/nginx/html/config.js.template > /usr/share/nginx/html/config.js

# Generate nginx.conf from template
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start nginx
exec nginx -g "daemon off;"