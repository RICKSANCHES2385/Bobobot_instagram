# Setup script for bobobot_inst_ddd project (Windows PowerShell)

Write-Host "🚀 Setting up bobobot_inst_ddd project..." -ForegroundColor Green

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow

# Create virtual environment
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv

# Activate virtual environment
Write-Host "✅ Activating virtual environment..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install -e ".[dev]"

# Copy .env.example to .env
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env file with your configuration" -ForegroundColor Yellow
}

# Start Docker infrastructure
Write-Host "🐳 Starting Docker infrastructure..." -ForegroundColor Cyan
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Run migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Cyan
alembic upgrade head

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Cyan
pytest

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration"
Write-Host "2. Start development: python -m src.main"
Write-Host "3. Run tests: pytest"
Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Green
