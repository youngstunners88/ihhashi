# Frontend Dockerfile for iHhashi
# Multi-stage build for optimized production image

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine as builder

WORKDIR /app

# Install dependencies first (for caching)
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Copy source and build
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_POSTHOG_KEY
ARG VITE_GOOGLE_MAPS_API_KEY
ARG VITE_PAYSTACK_PUBLIC_KEY
ARG VITE_SENTRY_DSN

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY \
    VITE_POSTHOG_KEY=$VITE_POSTHOG_KEY \
    VITE_GOOGLE_MAPS_API_KEY=$VITE_GOOGLE_MAPS_API_KEY \
    VITE_PAYSTACK_PUBLIC_KEY=$VITE_PAYSTACK_PUBLIC_KEY \
    VITE_SENTRY_DSN=$VITE_SENTRY_DSN

# Build the application
RUN npm run build

# ============================================
# Production Stage
# ============================================
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Create cache directories
RUN mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
