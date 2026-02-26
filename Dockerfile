# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY vite.config.js ./
COPY index.html ./
COPY src/ ./src/
COPY public/ ./public/
RUN npm run build

# Stage 2: Production
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /app/dist ./dist

# Environment
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV APP_DEBUG=false
ENV LOG_LEVEL=INFO

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
