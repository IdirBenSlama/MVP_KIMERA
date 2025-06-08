#!/bin/bash

echo "🚀 Deploying KIMERA SWM MVP..."

# Build and start services
docker-compose -f docker/docker-compose.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services..."
sleep 30

# Run health checks
echo "🔍 Running health checks..."
curl -f http://localhost:8000/system/status || exit 1
curl -f http://localhost:3000 || exit 1

echo "✅ KIMERA SWM MVP deployed successfully!"
echo "📊 API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
