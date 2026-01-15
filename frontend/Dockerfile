# Multi-stage Dockerfile for Retail Kiosk Frontend Service
# Based on Node.js 18 for building and Nginx for production serving

# ============================================================================
# Stage 1: Builder - Install dependencies and build
# ============================================================================
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Install system dependencies for node-gyp if needed
RUN apk add --no-cache python3 make g++

# Copy package files for better layer caching
COPY package*.json ./

# Install dependencies
RUN npm ci --silent --prefer-offline --no-audit

# Copy application source
COPY . .

# Build the application
RUN npm run build

# ============================================================================
# Stage 2: Runtime - Create minimal production image with Nginx
# ============================================================================
FROM nginx:1.25-alpine

# Set environment variables
ENV NODE_ENV=production

# Install curl for health checks
RUN apk add --no-cache curl

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -h /usr/share/nginx/html -s /sbin/nologin -G appuser -g appuser appuser

# Copy custom nginx configuration
COPY --chown=appuser:appuser <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy (optional - if backend is on different host)
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Copy built application from builder stage
COPY --from=builder --chown=appuser:appuser /app/dist /usr/share/nginx/html

# Adjust nginx to run as non-root
RUN touch /var/run/nginx.pid && \
    chown -R appuser:appuser /var/run/nginx.pid \
    /var/cache/nginx \
    /var/log/nginx \
    /etc/nginx/conf.d \
    /usr/share/nginx/html

# Switch to non-root user
USER appuser

# Expose port 80 for Nginx
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
