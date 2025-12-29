# Frontend Dockerfile for production
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# 使用 npm install 而不是 npm ci，以便自动更新 package-lock.json
RUN npm install

# Copy source code
COPY . .

# Build the application (不需要在构建时注入环境变量，使用运行时配置)
ENV VITE_MODE=production
RUN npm run build

# Production stage
FROM nginx:alpine

# Install gettext for envsubst
RUN apk add --no-cache gettext

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx template and config template
COPY nginx.conf.template /etc/nginx/nginx.conf.template
# Copy config template from build stage (since it's in the source code)
COPY --from=build /app/public/config.js.template /usr/share/nginx/html/config.js.template

# Copy docker entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set default environment variables (可以在 docker-compose.yml 中覆盖)
ENV BACKEND_HOST=backend
ENV BACKEND_PORT=8000
ENV VITE_SILICONFLOW_BASE_URL=http://backend:8000/api
ENV VITE_SILICONFLOW_API_KEY=sk-vbejswkfqhmfkslsfluyhhrlamxdhtzonsundldhjfjecfxi
ENV VITE_API_BASE_URL=

EXPOSE 80
CMD ["/docker-entrypoint.sh"]