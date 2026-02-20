# Quick start script for Mazingame web deployment (Windows PowerShell)

Write-Host "🎮 Mazingame Web Deployment" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is installed
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ docker-compose is installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose is not installed." -ForegroundColor Red
    Write-Host "   It should be included with Docker Desktop." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create data directory if it doesn't exist
if (-not (Test-Path "data")) {
    Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" | Out-Null
}

if (-not (Test-Path "logs")) {
    Write-Host "📁 Creating logs directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

Write-Host ""
Write-Host "🚀 Starting Mazingame web service..." -ForegroundColor Cyan
Write-Host ""

# Build and start the service
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Failed to start service. Check logs with:" -ForegroundColor Red
    Write-Host "   docker-compose logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting for service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if service is running
$status = docker-compose ps
if ($status -match "Up") {
    Write-Host ""
    Write-Host "✅ Mazingame web service is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access the game at: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Useful commands:" -ForegroundColor Yellow
    Write-Host "   View logs:        docker-compose logs -f"
    Write-Host "   Stop service:     docker-compose down"
    Write-Host "   Restart service:  docker-compose restart"
    Write-Host "   View stats:       curl http://localhost:5000/api/stats"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to start service. Check logs with:" -ForegroundColor Red
    Write-Host "   docker-compose logs" -ForegroundColor Yellow
    exit 1
}

# Made with Bob
